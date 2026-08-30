import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


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

        logger.info("INSTAGRAM_GEN | generate | instruction=%r", instruction)

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

            Rules specifically for IMAGE_PROMPT:

            - The image is a photo/scene only. It must NOT contain
              any logo, brand name, watermark, badge, text overlay,
              caption text, sign, label, or lettering of any kind —
              not on packaging, screens, clothing, signage, or
              anywhere else in the scene. Describe people, setting,
              props, mood, and lighting only.
            - Do not mention "Nexa Bank" or any bank name inside the
              IMAGE_PROMPT itself. The real Nexa Bank logo is added
              afterward by a separate, exact compositing step — if
              the prompt asks the model to draw a bank name or logo,
              it will invent its own incorrect one instead.
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
        else:
            logger.warning(
                "INSTAGRAM_GEN | generate | LLM output missing "
                "IMAGE_PROMPT: marker, image_prompt will be empty"
            )

        logger.info(
            "INSTAGRAM_GEN | generate | caption=%r | image_prompt=%r",
            caption.strip(), image_prompt.strip(),
        )

        return {
            "caption": caption.strip(),
            "image_prompt": image_prompt.strip(),
        }