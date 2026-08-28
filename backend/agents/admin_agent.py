import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from agents.admin_sql_agent import AdminSQLAgent
from agents.tools.email_generator_tool import EmailGeneratorTool


class AdminAgent:

    def __init__(self):

        self.llm = ChatOpenAI(
            model="gpt-5-mini",
            temperature=0,
        )

        self.sql_agent = AdminSQLAgent()

        self.email_generator = EmailGeneratorTool()

    # ---------------------------------------------------
    # Decide what tools are required
    # ---------------------------------------------------

    def _plan(self, question: str) -> dict:

        prompt = ChatPromptTemplate.from_template(
            """
            You are the supervisor of a banking admin AI system.

            Determine which capabilities are needed to complete
            the administrator's request.

            Available capabilities:

            1. SQL
               Query banking customers, accounts, loans and cards.

            2. EXCEL
               Generate Excel reports from SQL results.

            3. EMAIL
               Prepare customer emails.

            4. INSTAGRAM
               Prepare social media campaigns.

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
            return json.loads(content)

        except json.JSONDecodeError:

            return {
                "sql_required": False,
                "excel_required": False,
                "email_required": False,
                "instagram_required": False,
            }

    # ---------------------------------------------------
    # Extract email addresses from SQL result
    # ---------------------------------------------------

    def _extract_emails(
        self,
        rows: list[dict],
    ) -> list[str]:

        emails = []

        for row in rows:

            email = row.get("email")

            if email:
                emails.append(email)

        return list(set(emails))

    # ---------------------------------------------------
    # Main Agent
    # ---------------------------------------------------

    def query(
        self,
        question: str,
    ) -> dict:

        plan = self._plan(question)

        result = {
            "question": question,
            "plan": plan,
            "sql_query": "",
            "rows": [],
            "answer": "",
            "email": None,
            "approval_required": False,
        }

        # -------------------------------------------
        # SQL
        # -------------------------------------------

        if plan.get("email_required"):
            sql_instruction = (
                "The result will be used for sending emails. "
                "Always include users.email in the SELECT result."
            )

            sql_result = self.sql_agent.query(
                question,
                additional_instruction=sql_instruction,

            )

            result["sql_query"] = sql_result.get(
                "sql_query",
                "",
            )

            result["rows"] = sql_result.get(
                "rows",
                [],
            )

            result["answer"] = sql_result.get(
                "answer",
                "",
            )

        # -------------------------------------------
        # EMAIL
        # -------------------------------------------

        if plan.get("email_required"):

            recipients = []

            if result["rows"]:

                recipients = self._extract_emails(
                    result["rows"]
                )

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

            result["email"] = {
                "recipients": recipients,
                "recipient_count": len(recipients),
                "subject": email["subject"],
                "body": email["body"],
                "status": "DRAFT",
            }

            result["approval_required"] = True

        return result