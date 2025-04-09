# backend/layout_agent.py

import re
from langchain_core.prompts import PromptTemplate

class LayoutAgent:
    """
    Decides which sections the site requires, in a sensible order, 
    by prompting the LLM with a system + human prompt.
    """

    def __init__(self, llm):
        """
        llm: An LLM instance, such as ChatGoogleGenerativeAI or OpenAI.
        """
        self.llm = llm

        # The system prompt: sets the role/context of the LLM
        system_prompt = """\
                        You are a web design expert.
                        Your task is to suggest sections for a website, given a particular purpose.

                        Strict Rule:
                        - If the user provided section names, return only those — unless their request clearly asks for more.
                        - If no sections are provided, then generate a sensible layout based on the website type and purpose.

                        Always respond with a comma-separated list of section names (no extra text).
                        """


        # The human prompt in Jinja2 format:
        # - If user provided sections, we mention them.
        # - If no sections are provided, we request a complete set from scratch.
        human_prompt = """\
                        Client needs a website for: {{ purpose }}.
                        Website type should be: {{ website_type }}
                        
                        {% if sections %}
                        Use ONLY these sections unless the user explicitly asks for more:
                        {{ sections }}
                        {% else %}
                        Generate a complete section list appropriate for this site type.
                        {% endif %}
                        """


        # We combine system + human instructions into one final text,
        # then parse it as a Jinja2 template. 
        # This is purely a style choice – you could also do two separate messages if you prefer.
        full_prompt_text = system_prompt + "\n" + human_prompt
        
        # Create a PromptTemplate from the combined text
        self.prompt = PromptTemplate.from_template(
            full_prompt_text,
            template_format="jinja2"
        )

        # We'll store the chain as well, so we can do self.chain.invoke(...)
        # or if you have a pipeline that is prompt → LLM, you can do something like:
        self.chain = self.prompt | self.llm

    def decide_layout(self, user_purpose: str, user_sections: list, website_type: str) -> list:
        """
        1) Fills the Jinja2 template with `purpose` and `sections`.
        2) Calls the LLM, which returns a comma-separated string of sections.
        3) Cleans the string, returns a deduplicated list (title-cased).
        """

        # Convert list to comma-separated string (for the Jinja2 prompt).
        sections_str = ", ".join(user_sections) if user_sections else ""

        # "invoke" the chain with the variables needed for the template.
        response = self.chain.invoke({
            "purpose": user_purpose,
            "sections": sections_str,
            "website_type": website_type
        }).content  # .content is the final text from the LLM

        # Now, we parse the LLM's output. It's comma-separated, 
        # but it might also contain bullet points, or random punctuation, so let's do a quick cleanup.
        # For example, "Hero, About, Contact,   Footer" → ["Hero","About","Contact","Footer"]
        # Also, we do a simple dedup by converting to a dict then back to list.
        sections = re.split(r'[,\n;]+', response)  # split on commas, newlines, semicolons
        cleaned = [s.strip().title() for s in sections if s.strip()]

        # Deduplicate while preserving order:
        unique_sections = list(dict.fromkeys(cleaned))
        
        return unique_sections