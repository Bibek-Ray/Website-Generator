from langchain_core.prompts import ChatPromptTemplate

class CodeCleanerAgent:
    """Cleans the final HTML and CSS codes and provides a critique if needed."""

    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                (
                    "You are a code cleaner and critic. Your job is to remove any syntactical or grammatical errors, "
                    "improve the aesthetics of the code, and return only the cleaned HTML and CSS code. "
                    "Do NOT wrap the cleaned HTML code in ```html ... ``` and the cleaned CSS code in ```css ... ```."
                )
            ),
            (
                "human",
                "HTML Code: {html_code}\nCSS Code: {css_code}"
            )
        ])

    def start_cleaning(self, html_code, css_code):
        # Attempt to extract code between markdown fences if present
        try:
            if "```html" in html_code:
                html_code = html_code.split("```html")[1].split("```")[0].strip()
            else:
                html_code = html_code.strip()
        except Exception as e:
            print("Error extracting HTML code:", e)
            html_code = html_code.strip()

        try:
            if "```css" in css_code:
                css_code = css_code.split("```css")[1].split("```")[0].strip()
            else:
                css_code = css_code.strip()
        except Exception as e:
            print("Error extracting CSS code:", e)
            css_code = css_code.strip()

        # Create the chain by piping the prompt to the LLM
        chain = self.prompt | self.llm

        # Invoke the chain with the provided HTML and CSS code
        response = chain.invoke({
            "html_code": html_code,
            "css_code": css_code
        }).content

        # Attempt to extract cleaned HTML and CSS from the response
        cleaned_html = ""
        cleaned_css = ""
        try:
            if "```html" in response:
                cleaned_html = response.split("```html")[1].split("```")[0].strip()
            else:
                cleaned_html = response.strip()
        except Exception as e:
            print("Error parsing cleaned HTML code:", e)
            cleaned_html = response.strip()

        try:
            if "```css" in response:
                cleaned_css = response.split("```css")[1].split("```")[0].strip()
            else:
                cleaned_css = ""
        except Exception as e:
            print("Error parsing cleaned CSS code:", e)
            cleaned_css = ""

        return cleaned_html, cleaned_css