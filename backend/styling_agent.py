# backend/styling_agent.py
from langchain_core.prompts import ChatPromptTemplate

class StylingAgent:
    """Generates theme-appropriate styling by prompting an LLM."""
    
    def __init__(self, llm):
        self.llm = llm
        # Define a system prompt to set the role and instruct the LLM
        # Then a human prompt that provides additional context (website purpose)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a creative web design expert. 
                          Generate a color scheme and styling details for a website with a {theme} theme. 
                          Return your answer as valid JSON with keys:
                          background_color, text_color, primary_color, secondary_color, accent_color, 
                          font_family (web-safe), button_style (css)."""),
            ("human", "Website purpose: {purpose}")
        ])

    def choose_styling(self, user_theme, user_purpose):
        chain = self.prompt | self.llm
        response = chain.invoke({
            "theme": user_theme,
            "purpose": user_purpose
        }).content
        
        # Attempt to extract JSON from the response.
        try:
            # Look for the JSON block (if wrapped in markdown for example)
            json_str = response.split("```json")[1].split("```")[0]
            return eval(json_str)  # For simplicity; consider using json.loads() in production.
        except Exception as e:
            print("Error parsing JSON response:", e)
            # Fallback to a default styling if parsing fails
            return {
                "background_color": "#ffffff",
                "text_color": "#333333",
                "primary_color": "#2563eb",
                "secondary_color": "#e2e8f0",
                "accent_color": "#f56565",
                "font_family": "system-ui, sans-serif",
                "button_style": "border: none; padding: 10px 20px; cursor: pointer;"
            }
