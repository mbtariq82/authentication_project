import json
import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from agents.admin_sql_agent import AdminSQLAgent
from agents.excel_export import save_query_result_workbook
from agents.tools.email_generator_tool import EmailGeneratorTool
from agents.tools.instagram_generator_tool import InstagramGeneratorTool
from agents.tools.image_generator_tool import ImageGeneratorTool
from agents.services.approval_service import approval_service

logger = logging.getLogger(__name__)


class AdminAgent:

    def __init__(self):

        self.llm = ChatOpenAI(
            model="gpt-5-mini",
            temperature=0,
        )

        self.sql_agent = AdminSQLAgent()

        self.email_generator = EmailGeneratorTool()
        self.instagram_generator = InstagramGeneratorTool()
        self.image_generator = ImageGeneratorTool()

        logger.info("AdminAgent initialized")

    # ---------------------------------------------------
    # Decide what tools are required
    # ---------------------------------------------------

    def _plan(self, question: str) -> dict:

        logger.info("PLAN | question=%r", question)

        prompt = ChatPromptTemplate.from_template(
            """
            You are the supervisor of a banking admin AI system.

            Determine which capabilities are needed to complete
            the administrator's request. A single request can need
            more than one capability at once.

            Available capabilities:

            1. SQL
               Query banking customers, accounts, loans and cards.

            2. EXCEL
               Generate Excel reports from SQL results.
               (Implies SQL is also required.)

            3. EMAIL
               Prepare customer emails (e.g. promotions, festival
               greetings, notices). Requires human approval before
               sending, so this only drafts the email.
               (Implies SQL is required if the email needs to target
               specific customers.)

            4. INSTAGRAM
               Prepare a social media post. Requires human approval
               before publishing, so this only drafts the post.

            Request:

            {question}

            Return ONLY valid JSON.

            Format:

            {{
                "sql_required": true,
                "excel_required": false,
                "email_required": false,
                "instagram_required": false
            }}

            Examples:

            Request:
            Show customers whose balance is above 5000

            {{
                "sql_required": true,
                "excel_required": false,
                "email_required": false,
                "instagram_required": false
            }}

            Request:
            Show customers whose balance is 0

            {{
                "sql_required": true,
                "excel_required": false,
                "email_required": false,
                "instagram_required": false
            }}

            Request:
            Prepare a promotional email for all customers

            {{
                "sql_required": false,
                "excel_required": false,
                "email_required": true,
                "instagram_required": false
            }}

            Request:
            Find customers whose balance is above 5000
            and prepare an email for them

            {{
                "sql_required": true,
                "excel_required": false,
                "email_required": true,
                "instagram_required": false
            }}

            Request:
            Create an Excel report of customers with zero balance

            {{
                "sql_required": true,
                "excel_required": true,
                "email_required": false,
                "instagram_required": false
            }}

            Request:
            Give me a list of customers with zero balance as text
            and also as an Excel report

            {{
                "sql_required": true,
                "excel_required": true,
                "email_required": false,
                "instagram_required": false
            }}

            Request:
            Create an Instagram post about our new festival offer

            {{
                "sql_required": false,
                "excel_required": false,
                "email_required": false,
                "instagram_required": true
            }}
            """
        )

        chain = prompt | self.llm

        response = chain.invoke(
            {
                "question": question
            }
        )

        content = (
            response.content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        try:
            plan = json.loads(content)

        except json.JSONDecodeError:
            logger.warning(
                "PLAN | could not parse planner output as JSON, "
                "defaulting to no-op plan: %r",
                content,
            )

            return {
                "sql_required": False,
                "excel_required": False,
                "email_required": False,
                "instagram_required": False,
            }

        # EXCEL and (targeted) EMAIL both need query results to work
        # with, so make sure sql_required is on whenever they are —
        # don't rely solely on the model to have set it correctly.
        if plan.get("excel_required") or plan.get("email_required"):
            plan["sql_required"] = True

        logger.info("PLAN | result=%s", plan)

        return plan

    # ---------------------------------------------------
    # Extract email addresses from SQL result
    # ---------------------------------------------------

    def _extract_emails(
        self,
        rows: list[dict],
    ) -> list[str]:
        """
        Pulls email addresses out of SQL result rows.

        The SQL agent's LLM doesn't always alias the column back as
        exactly "email" (it might come back as "Email", "user_email",
        etc.), so a naive row.get("email") silently returns nothing
        in those cases — the request looks successful but ends up
        with 0 recipients. This matches case-insensitively first,
        then falls back to any column whose name merely contains
        "email", and validates each value looks like an address
        before including it.
        """

        emails: set[str] = set()

        for row in rows:

            value = self._find_email_value(row)

            if value and "@" in value:
                emails.add(value.strip())

        logger.info(
            "EXTRACT_EMAILS | rows=%d | emails_found=%d",
            len(rows), len(emails),
        )

        if rows and not emails:
            logger.warning(
                "EXTRACT_EMAILS | rows were returned but no email "
                "column was found | sample_row_keys=%s",
                list(rows[0].keys()) if rows else [],
            )

        return list(emails)

    @staticmethod
    def _find_email_value(row: dict) -> str | None:

        # Exact match first (the common, expected case).
        if "email" in row and row["email"]:
            return str(row["email"])

        # Case-insensitive exact match, e.g. "Email".
        for key, value in row.items():
            if key.lower() == "email" and value:
                return str(value)

        # Fallback: any column whose name merely contains "email",
        # e.g. "user_email", "customer_email".
        for key, value in row.items():
            if "email" in key.lower() and value:
                return str(value)

        return None

    # ---------------------------------------------------
    # Main Agent
    # ---------------------------------------------------

    def query(
        self,
        question: str,
        created_by: str | None = None,
    ) -> dict:

        logger.info("QUERY START | created_by=%s | question=%r", created_by, question)

        plan = self._plan(question)

        result = {
            "question": question,
            "plan": plan,
            "sql_query": "",
            "rows": [],
            "answer": "",
            "excel_file": None,
            "email": None,
            "instagram": None,
            "approvals": [],
        }

        # -------------------------------------------
        # SQL — runs whenever SQL, Excel, or a
        # customer-targeted email needs data.
        # -------------------------------------------

        if plan.get("sql_required"):

            logger.info("SQL | running (sql_required=True)")

            sql_instruction = ""

            if plan.get("email_required"):
                sql_instruction = (
                    "The result will be used for sending emails. "
                    "The SELECT list MUST include the users.email "
                    "column, aliased to exactly the lowercase column "
                    "name 'email' (e.g. \"users.email AS email\"), "
                    "with no other alias or casing. If the admin's "
                    "question names a specific customer, filter for "
                    "that customer explicitly (by name and/or email) "
                    "rather than returning unrelated rows — if no "
                    "matching customer exists, return zero rows "
                    "rather than guessing."
                )

            sql_result = self.sql_agent.query(
                question,
                additional_instruction=sql_instruction,
            )

            result["sql_query"] = sql_result.get("sql_query", "")
            result["rows"] = sql_result.get("rows", [])
            result["answer"] = sql_result.get("answer", "")

            logger.info(
                "SQL | done | rows=%d | sql=%s",
                len(result["rows"]), result["sql_query"],
            )
        else:
            logger.info("SQL | skipped (sql_required=False)")

        # -------------------------------------------
        # EXCEL
        # -------------------------------------------

        if plan.get("excel_required"):

            logger.info("EXCEL | building workbook | rows=%d", len(result["rows"]))

            filename = save_query_result_workbook(
                rows=result["rows"],
                question=question,
                sql_query=result["sql_query"],
                answer=result["answer"],
            )

            result["excel_file"] = {
                "filename": filename,
                "download_url": f"/admin/download/{filename}",
            }

            logger.info("EXCEL | saved | filename=%s", filename)

        # -------------------------------------------
        # EMAIL — draft only. Actual sending happens
        # from the /admin/approve/{id} endpoint once a
        # human approves it.
        # -------------------------------------------

        if plan.get("email_required"):

            logger.info("EMAIL | drafting")

            recipients = []

            if result["rows"]:
                recipients = self._extract_emails(result["rows"])

            customer_context = ""

            if result["rows"]:
                customer_context = (
                    f"The SQL query selected "
                    f"{len(result['rows'])} customers."
                )

            email = self.email_generator.generate(
                instruction=question,
                customer_context=customer_context,
            )

            approval = approval_service.create(
                action_type="email",
                payload={
                    "recipients": recipients,
                    "subject": email["subject"],
                    "body": email["body"],
                },
                created_by=created_by,
            )

            result["email"] = {
                "recipients": recipients,
                "recipient_count": len(recipients),
                "subject": email["subject"],
                "body": email["body"],
                "status": "PENDING_APPROVAL",
                "approval_id": approval["id"],
            }

            result["approvals"].append(approval["id"])

            logger.info(
                "EMAIL | drafted | approval_id=%s | recipients=%d | subject=%r",
                approval["id"], len(recipients), email["subject"],
            )

        # -------------------------------------------
        # INSTAGRAM — draft only. Actual publishing
        # happens from /admin/approve/{id} once a human
        # approves it.
        # -------------------------------------------

        if plan.get("instagram_required"):

            logger.info("INSTAGRAM | drafting")

            post = self.instagram_generator.generate(instruction=question)

            image_url = None

            try:
                image_url = self.image_generator.generate(
                    post["image_prompt"]
                )
                logger.info("INSTAGRAM | image generated | url=%s", image_url)
            except Exception:
                # Image generation is best-effort. If it fails (bad
                # API key, content policy rejection, network issue),
                # fall through with no image — the admin can attach
                # one manually when approving.
                logger.exception(
                    "INSTAGRAM | image generation failed, "
                    "continuing without an image_url"
                )

            approval = approval_service.create(
                action_type="instagram",
                payload={
                    "caption": post["caption"],
                    "image_prompt": post["image_prompt"],
                    "image_url": image_url,
                },
                created_by=created_by,
            )

            result["instagram"] = {
                "caption": post["caption"],
                "image_prompt": post["image_prompt"],
                "image_url": image_url,
                "status": "PENDING_APPROVAL",
                "approval_id": approval["id"],
            }

            result["approvals"].append(approval["id"])

            logger.info(
                "INSTAGRAM | drafted | approval_id=%s | has_image=%s",
                approval["id"], image_url is not None,
            )

        result["approval_required"] = bool(result["approvals"])

        logger.info(
            "QUERY END | approvals=%s | approval_required=%s",
            result["approvals"], result["approval_required"],
        )

        return result