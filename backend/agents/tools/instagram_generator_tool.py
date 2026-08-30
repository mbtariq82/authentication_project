from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class InstagramGeneratorTool:

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-5-mini",
            temperature=0.5,
        )

    def generate(
        self,
        instruction: str,
    ) -> dict:

        prompt = ChatPromptTemplate.from_template(
            """
            You are a social media content assistant
            for a retail bank.

            Admin request:
            {instruction}

            Create an Instagram post.

            Return:

            CAPTION:
            <caption>

            IMAGE_PROMPT:
            <description for generating the image>

            Rules:

            - Maintain a professional banking tone.
            - Do not invent interest rates or financial offers.
            - Do not make misleading financial claims.
            - Keep promotional wording clear and appropriate.
            """
        )

        chain = prompt | self.llm

        response = chain.invoke(
            {
                "instruction": instruction
            }
        )

        content = response.content.strip()

        caption = ""
        image_prompt = ""

        if "CAPTION:" in content:

            content = content.replace(
                "CAPTION:",
                "",
                1,
            )

        if "IMAGE_PROMPT:" in content:

            caption, image_prompt = content.split(
                "IMAGE_PROMPT:",
                1,
            )

        return {
            "caption": caption.strip(),
            "image_prompt": image_prompt.strip(),
        }
