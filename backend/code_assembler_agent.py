# backend/code_assembler_agent.py
import json
from langchain.schema import SystemMessage

class CodeAssemblerAgent:
    def __init__(self, llm=None):
        # Optionally, you can pass an LLM instance here.
        self.llm = llm

    def assemble_code(self, section_layout, style_info, copy_info):
        if self.llm:
            prompt = f"""
You are a skilled web developer. Your task is to generate a complete HTML website and corresponding CSS file using the following components.

Section Layout (in order): {section_layout}

Style Information (JSON):
{json.dumps(style_info, indent=2)}

Copy Information (JSON):
{json.dumps(copy_info, indent=2)}

Generate:
1. A complete HTML file that includes:
   - A proper DOCTYPE declaration.
   - A <head> section with a link to an external CSS file ("styles.css") and a <title> taken from the 'Hero' section if available.
   - A <body> that contains a section for each entry in the section layout. Each section should incorporate its corresponding copy information.
2. A separate CSS file that styles the page using the provided style information.

Separate the HTML and CSS outputs with the delimiter: ###CSS###

Respond ONLY with the final output.
"""
            # Pass the prompt string directly.
            response = self.llm.invoke(prompt).content
            try:
                html, css = response.split("###CSS###")
                return html.strip(), css.strip()
            except Exception as e:
                print("Error parsing LLM output:", e)
                return response, ""
        else:
            # Fallback to the deterministic, template-based approach.
            html = [f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{copy_info.get('Hero', {}).get('title', 'Generated Site')}</title>
    <link rel="stylesheet" href="styles.css" />
</head>
<body>"""]

            for section in section_layout:
                content = copy_info.get(section, {})
                html.append(f'<section class="{section.lower()}-section">')
                if 'title' in content:
                    html.append(f'<h2>{content["title"]}</h2>')
                if 'items' in content:
                    html.append('<div class="items-container">')
                    for item in content["items"]:
                        html.append(f"""<div class="item">
    <h3>{item.get('title', '')}</h3>
    <p>{item.get('description', '')}</p>
</div>""")
                    html.append('</div>')
                elif 'content' in content:
                    html.append(f'<p>{content["content"]}</p>')
                html.append('</section>')

            html.append('</body>')
            html.append('</html>')
            css = self._generate_css(style_info)
            return '\n'.join(html), css

    def _generate_css(self, style_info):
        return f"""
body {{
    background-color: {style_info.get('background_color', '#ffffff')};
    color: {style_info.get('text_color', '#333333')};
    font-family: {style_info.get('font_family', 'system-ui, sans-serif')};
    line-height: 1.6;
    margin: 0;
    padding: 20px;
}}

section {{
    padding: 40px 0;
    max-width: 1200px;
    margin: 0 auto;
}}

.items-container {{
    display: grid;
    gap: 30px;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}}

button {{
    background: {style_info.get('primary_color', '#2563eb')};
    color: white;
    padding: 12px 25px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}}
"""
