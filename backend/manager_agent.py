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

class ManagerAgent:
    def __init__(self):
        # Create the LLM for the Manager
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.7,
            verbose=True
        )
        self.layout_agent = LayoutAgent(self.llm)
        self.styling_agent = StylingAgent(self.llm)
        self.copywriting_agent = CopywritingAgent(self.llm)
        self.assembler_agent = CodeAssemblerAgent(self.llm)
        self.cleaner_agent = CodeCleanerAgent(self.llm)

    def generate_site(self, user_prompt: str):
        # The system prompt: instruct the LLM how to parse the user prompt
        system_prompt = """You are a Manager Agent. 
Your job is to analyze the user's prompt and break it into tasks for:
1) Layout Agent 
2) Styling Agent 
3) Copywriting Agent
4) Assembler Agent

Specifically, parse the user’s request into:
- user_theme (e.g. 'dark' or 'light')
- user_purpose (short description, e.g. 'SaaS landing page', 'Personal portfolio')
- user_sections (a list of key sections for the website, e.g. ["Hero","Projects","Contact","Footer"])

Return these in a JSON object with keys: user_theme, user_purpose, user_sections.
Example output:
{
  "user_theme": "dark",
  "user_purpose": "Personal Portfolio",
  "user_sections": ["Hero","Projects","Contact","Footer"]
}


"""
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
            print("Manager Agent succesfully designating task...")
            data = json.loads(json_str)
            user_theme = data.get("user_theme", "light")
            user_purpose = data.get("user_purpose", "Generic Website")
            user_sections = data.get("user_sections", [])
        except Exception as e:
            print("Error parsing manager output:", e)
            user_theme = "light"
            user_purpose = "Generic Website"
            user_sections = []

        print(f"User Theme: {user_theme} \nUser Purpose: {user_purpose} \nUser Sections: {user_sections}")
        section_layout = self.layout_agent.decide_layout(user_purpose, user_sections)
        style_info = self.styling_agent.choose_styling(user_theme, user_purpose)
        copy_info = self.copywriting_agent.generate_copy(user_purpose, section_layout)
        beta_html, beta_css = self.assembler_agent.assemble_code(section_layout, style_info, copy_info)
        final_html, final_css = self.cleaner_agent.start_cleaning(beta_html, beta_css)
        return final_html, final_css