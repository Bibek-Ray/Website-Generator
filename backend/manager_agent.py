# backend/manager_agent.py

import os
import json
from langchain.schema import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.layout_agent import LayoutAgent
from backend.styling_agent import StylingAgent
from backend.copywriting_agent import CopywritingAgent
from backend.code_assembler_agent import CodeAssemblerAgent
from backend.code_cleaner_agent import CodeCleanerAgent
from backend.revision_agent import RevisionAgent
from typing import Tuple

class ManagerAgent:
    def __init__(self):
        # Initialize the LLM with your configuration
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.7,
            verbose=True
        )
        # Initialize all specialized agents
        self.layout_agent = LayoutAgent(self.llm)
        self.styling_agent = StylingAgent(self.llm)
        self.copywriting_agent = CopywritingAgent(self.llm)
        self.assembler_agent = CodeAssemblerAgent(self.llm)
        self.cleaner_agent = CodeCleanerAgent(self.llm)
        self.revision_agent = RevisionAgent(self.llm)
        
        # Store conversation state for iterative feedback/revisions
        self.conversation_state = {}

    def analyze_prompt(self, user_prompt: str):
        """
        Analyze the user's prompt and extract key parameters.
        Returns:
          - user_theme: 'dark' or 'light'
          - user_purpose: short description (e.g. 'Personal Portfolio')
          - user_sections: list of key website sections (e.g. ['Hero', 'Projects', 'Contact', 'Footer'])
        """
        system_prompt = (
            "You are a Manager Agent. Your job is to analyze the user's prompt and extract key details. "
            "Provide a JSON object with the following keys: website_type, user_theme, user_purpose, and user_sections. "
            "The website_type should reflect the kind of website the user wants (e.g., 'landing', 'blog', 'ecommerce', 'portfolio', etc.). "
            "The user_theme should be depend on the user's prompt and if not provided select what you think suits the user_purpose. "
            "The user_purpose is a brief description of the website's goal. "
            "The user_sections is a list of essential website sections."
        )
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response_text = self.llm(messages).content

        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        else:
            json_str = response_text
        
        try:
            data = json.loads(json_str)
            website_type = data.get("website_type", "landing")
            user_theme = data.get("user_theme", "light")
            user_purpose = data.get("user_purpose", "Generic Website")
            user_sections = data.get("user_sections", [])
        except Exception as e:
            print("Error parsing analysis output:", e)
            user_theme = "light"
            website_type = "landing"
            user_purpose = "Generic Website"
            user_sections = []
        
        return website_type, user_theme, user_purpose, user_sections

    def generate_site(self, user_prompt: str):
        """
        Fully generate the website by:
          1. Analyzing the prompt.
          2. Determining the layout.
          3. Generating style info.
          4. Producing copy for each section.
          5. Assembling HTML/CSS.
          6. Cleaning the final output.
        Returns the final HTML and CSS.
        """
        # Step 1: Analyze prompt
        website_type, user_theme, user_purpose, user_sections = self.analyze_prompt(user_prompt)
        print(f"Extracted Details - Website Type: {website_type}, Theme: {user_theme}, Purpose: {user_purpose}, Sections: {user_sections}")

        # Step 2: Get website layout
        section_layout = self.layout_agent.decide_layout(user_purpose, user_sections, website_type)
        print(f"Section Layout: {section_layout}")

        # Step 3: Get styling information
        style_info = self.styling_agent.choose_styling(user_theme, user_purpose)
        print(f"Style Information: {style_info}")

        # Step 4: Generate copy for each section
        copy_info = self.copywriting_agent.generate_copy(user_purpose, section_layout, website_type)
        print(f"Copy Information: {copy_info}")

        # Step 5: Assemble HTML and CSS
        beta_html, beta_css = self.assembler_agent.assemble_code(section_layout, style_info, copy_info, website_type)
        print("Assembled code generated.")

        # Step 6: Clean and finalize the code
        final_html, final_css = self.cleaner_agent.start_cleaning(beta_html, beta_css)
        print("Final cleaned code produced.")

        # Save the outputs in the conversation state for potential future revisions
        self.conversation_state = {
            "user_theme": user_theme,
            "website_type": website_type,
            "user_purpose": user_purpose,
            "user_sections": user_sections,
            "section_layout": section_layout,
            "style_info": style_info,
            "copy_info": copy_info,
            "html": final_html,
            "css": final_css
        }

        return final_html, final_css

    def revise_site(self, message: str, html: str, css: str) -> Tuple[str, str]:
        """
        Revise the current website based on user feedback.
        In this example, the feedback is simply appended as an HTML comment.
        A full implementation would call a dedicated RevisionAgent.
        """
        if not self.conversation_state.get("html"):
            print("No generated site available for revision.")
            return None, None

        # Example: Append feedback as a comment in the HTML body
        try:
            revised_html, revised_css = self.revision_agent.revise_code(message, html, css)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        self.conversation_state["html"] = revised_html
        self.conversation_state["css"] = revised_css
        return revised_html, revised_css