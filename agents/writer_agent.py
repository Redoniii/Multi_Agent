from dotenv import load_dotenv
import os
import json
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def writer_agent(notes, output_type="executive"):
    """
    Generate structured output with executive summary, email, and action list.
    Notes should be a list of dicts with 'text' and 'citation' fields.
    """
    # Check if notes indicate "not found" (research agent couldn't find relevant sources)
    if isinstance(notes, list) and len(notes) > 0:
        first_note = notes[0] if isinstance(notes[0], dict) else {}
        if first_note.get("supported") == False:
            return {
                "executive_summary": "NOT FOUND IN SOURCES - The query appears to be outside the domain of available supply chain documents.",
                "client_email": "Dear Client,\n\nUnfortunately, we were unable to find relevant information in our knowledge base to address your query. The topic appears to be outside the scope of our available supply chain management documents.\n\nSuggested Next Steps:\n- Provide additional context or rephrasing of your question\n- Clarify which supply chain topic (resilience, coordination, security, performance, etc.) your query relates to\n- Consider uploading additional documents if they exist\n\nWe've gathered what we could but cannot provide a confident answer without relevant source material.\n\nKind Regards,\nSupply Chain Analysis Team",
                "action_list": [{"owner": "Documentation Team", "due_date": "2026-02-23", "confidence": "N/A", "description": "Acquire or upload documents relevant to this query topic"}],
                "sources_cited": []
            }
    
    notes_text = ""
    if isinstance(notes, list):
        for note in notes:
            if isinstance(note, dict):
                notes_text += f"- {note.get('text', '')}\n  Citation: {note.get('citation', 'N/A')}\n"
            else:
                notes_text += f"- {note}\n"
    else:
        notes_text = str(notes)
    
    prompt = f"""
    You are a Writer Agent. Create a professional deliverable.
    
    Research Notes:
    {notes_text}
    
    Generate a JSON response with these exact fields:
    {{
        "executive_summary": "Max 150 words summarizing key findings",
        "client_email": "Professional email format with greeting and closing",
        "action_list": [
            {{"owner": "Team/Person", "due_date": "YYYY-MM-DD format", "confidence": "High|Medium|Low", "description": "Action item"}}
        ],
        "sources_cited": ["list of unique citations from research"]
    }}
    
    Ensure all claims are grounded in the research notes provided.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    
    result_text = response.choices[0].message.content
    
    try:
        if "```json" in result_text:
            json_str = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            json_str = result_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = result_text
        
        return json.loads(json_str)
    except json.JSONDecodeError:
        #Fallback: return structured dict with the raw response
        return {
            "executive_summary": result_text[:150],
            "client_email": f"Subject: Supply Chain Analysis\n\n{result_text}",
            "action_list": [{"owner": "Team", "due_date": "2026-03-01", "confidence": "Medium", "description": result_text[:100]}],
            "sources_cited": ["See research notes above"]
        }
