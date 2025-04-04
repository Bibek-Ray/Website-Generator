# backend/sse_callback.py

from langchain.callbacks.base import BaseCallbackHandler

class SSECallbackHandler(BaseCallbackHandler):
    """
    A callback handler that stores step-by-step agent reasoning
    (Thought, Action, Observation) so we can stream it afterward.
    """
    def __init__(self):
        self.messages = []

    def on_agent_action(self, action, **kwargs):
        # The "Thought" plus the chosen tool
        self.messages.append(f"Thought: {action.log}\n")
        self.messages.append(f"Action: {action.tool}\nAction Input: {action.tool_input}\n")

    def on_tool_end(self, output, **kwargs):
        self.messages.append(f"Observation: {output}\n")

    def on_agent_finish(self, finish, **kwargs):
        self.messages.append(f"Thought: {finish.log}\n")
