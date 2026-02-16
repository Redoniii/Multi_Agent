from dotenv import load_dotenv
import os
import json
from openai import OpenAI

#Load .env variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

#Initialize OpenAI client
client = OpenAI(api_key=api_key)

def planner_agent(user_task):
    """
    Planner agent decomposes a user task into ordered subtasks with agent assignments.
    Returns a structured plan as JSON.
    """
    prompt = f"""
    You are a Planner Agent for a multi-agent system.
    Decompose the user task into ordered subtasks.
    
    User Task: {user_task}
    
    Generate a JSON response with this exact format:
    {{
        "overall_goal": "Summary of what we're trying to accomplish",
        "subtasks": [
            {{"step": 1, "task": "Description", "agent": "Research", "priority": "High"}},
            {{"step": 2, "task": "Description", "agent": "Writer", "priority": "High"}}
        ],
        "dependencies": ["Research must complete before Writer starts"],
        "success_criteria": ["Achievement criteria..."]
    }}
    
    Consider:
    - What information do we need (Research)?
    - What deliverable format (Writer)?
    - What validation is needed (Verifier)?
    
    Be concise and actionable.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    
    result_text = response.choices[0].message.content
    
    # Try to parse as JSON
    try:
        if "```json" in result_text:
            json_str = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            json_str = result_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = result_text
        
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Fallback: return plan as text
        return {
            "overall_goal": user_task,
            "subtasks": [
                {"step": 1, "task": "Research the topic", "agent": "Research", "priority": "High"},
                {"step": 2, "task": "Generate deliverable", "agent": "Writer", "priority": "High"},
                {"step": 3, "task": "Verify accuracy", "agent": "Verifier", "priority": "High"}
            ],
            "plan_text": result_text
        }

