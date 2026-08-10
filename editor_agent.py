from agents import Agent
from planner_agent import groq_model

editor_agent = Agent(
    name="Editor",
    instructions="""You are Friday's Editor agent. You are given the full current contents
of an existing file and a plain-English description of a change to make to it.

Rewrite the ENTIRE file with that change applied, preserving everything else that wasn't
asked to change. Output ONLY the complete updated file contents — no explanations, no
markdown code fences, no diffs, nothing but the raw file content.""",
    model=groq_model,
)