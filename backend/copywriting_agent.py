import json
from langchain_core.prompts import ChatPromptTemplate

class CopywritingAgent:
    """Generates section text using an LLM."""
    
    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You're a professional copywriter. Write concise, engaging text for website sections."
            ),
            (
                "human",
                (
                    "Website purpose: {purpose}\n"
                    "Website style: {website_type}\n"
                    "Section to write: {section}\n"
                    "Write content as JSON with appropriate keys. For example, for the Features section, "
                    "you might respond with:\n"
                    "```json\n"
                    "{{\n"
                    '  "title": "Key Features",\n'
                    '  "items": [\n'
                    "    {{\n"
                    '      "title": "Feature 1",\n'
                    '      "description": "Description for Feature 1"\n'
                    "    }},\n"
                    "    {{\n"
                    '      "title": "Feature 2",\n'
                    '      "description": "Description for Feature 2"\n'
                    "    }}\n"
                    "  ]\n"
                    "}}\n"
                    "```\n"
                    "Respond ONLY with JSON (no extra commentary)."
                )
            )
        ])

    def generate_copy(self, user_purpose, section_layout, website_type):
        copy_data = {}
        for section in section_layout:
            chain = self.prompt | self.llm
            response = chain.invoke({
                "purpose": user_purpose,
                "section": section,
                "website_type": website_type
            }).content
            try:
                # If the LLM wraps the JSON in markdown, extract the JSON block.
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0].strip()
                else:
                    json_str = response
                copy_data[section] = json.loads(json_str)
            except Exception as e:
                print(f"Error parsing JSON for section '{section}':", e)
                copy_data[section] = {"content": response}
        return copy_data