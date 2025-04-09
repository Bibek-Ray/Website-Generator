from typing import Tuple
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json

class RevisionAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are an expert web developer AI.
                The user will give you feedback to revise a website.
                You will be given the full HTML and CSS of the current site.

                Based on the feedback, make only the necessary changes.
                Do not change anything else.
                Do not invent new sections unless explicitly asked.

                Return ONLY a JSON object with the following keys:
                - html: (modified HTML code)
                - css: (modified CSS code)
            """),
            ("human", """
                User Feedback:
                {feedback}

                ---
                Current HTML:
                {html}

                ---
                Current CSS:
                {css}
            """)
        ])

    @staticmethod
    def clean_code_block(code: str, lang: str) -> str:
        """Removes any ```lang fences from a string."""
        pattern = rf"```{lang}\s*(.*?)```"
        match = re.search(pattern, code, re.DOTALL)
        return match.group(1).strip() if match else code.strip()

    @staticmethod
    def strip_code_fences(s: str) -> str:
        """Removes triple-backtick fences like ```json ... ``` at start/end."""
        s = s.strip()
        if s.startswith("```"):
            s = re.sub(r"^```[a-zA-Z0-9]*\n?", "", s)
        if s.endswith("```"):
            s = s[:-3]
        return s.strip()

    def revise_code(self, feedback: str, html: str, css: str) -> Tuple[str, str]:
        chain = self.prompt | self.llm | StrOutputParser()
        raw_output = chain.invoke({"feedback": feedback, "html": html, "css": css})

        # Use the static method from this class
        raw_output_stripped = self.strip_code_fences(raw_output)

        try:
            result = json.loads(raw_output_stripped)
            print("Revised Code: ", result)

            # Use the static method from this class
            clean_html = self.clean_code_block(result.get("html", html), "html")
            clean_css = self.clean_code_block(result.get("css", css), "css")

            return (clean_html, clean_css)
        except Exception as e:
            print("Failed to parse LLM revision output:", e)
            print("Raw Output:\n", raw_output)
            return html, css