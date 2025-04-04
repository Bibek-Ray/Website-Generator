# backend/generator.py

import os

from manager_agent import ManagerAgent

def generate_frontend_site(user_prompt):
    """
    Instantiates the ManagerAgent and calls generate_site.
    Returns (html_string, css_string).
    """
    agent = ManagerAgent()
    html, css = agent.generate_site(user_prompt)
    return html, css

def save_generated_site(site_id, html, css):
    """
    Save the output to /generated_sites/site_xxx/
    """
    # Ensure the directory exists
    output_dir = f"generated_sites/site_{site_id}"
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    with open(os.path.join(output_dir, "styles.css"), "w", encoding="utf-8") as f:
        f.write(css)

    return output_dir
