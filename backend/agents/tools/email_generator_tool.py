import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class EmailGeneratorTool:

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-5-mini",
            temperature=0.3,
        )

    def generate(
        self,
        instruction: str,
        customer_context: str = "",
    ) -> dict:

        logger.info(
            "EMAIL_GEN | generate | instruction=%r | customer_context=%r",
            instruction, customer_context,
        )

        prompt = ChatPromptTemplate.from_template(
            """
            You are an email assistant for a banking administrator.

            Create a professional customer email.

            Admin instruction:
            {instruction}

            Customer / query context:
            {customer_context}

            Return the response exactly in this format:

            SUBJECT:
            <subject>

            BODY:
            <email body>

            Rules:

            - Do not invent banking offers, interest rates or fees.
            - Do not promise products or benefits that were not provided
              by the administrator.
            - Keep the tone professional and customer friendly.
            - Do not include sensitive customer information.
            """
        )

        chain = prompt | self.llm

        response = chain.invoke(
            {
                "instruction": instruction,
                "customer_context": customer_context,
            }
        )

        content = response.content.strip()

        subject = ""
        body = content

        if "SUBJECT:" in content and "BODY:" in content:

            subject_part, body_part = content.split(
                "BODY:",
                1,
            )

            subject = (
                subject_part
                .replace("SUBJECT:", "")
                .strip()
            )

            body = body_part.strip()
        else:
            logger.warning(
                "EMAIL_GEN | generate | LLM output did not contain "
                "expected SUBJECT:/BODY: markers, using raw content as body"
            )

        logger.info("EMAIL_GEN | generate | subject=%r", subject)

        return {
            "subject": subject,
            "body": body,
        }