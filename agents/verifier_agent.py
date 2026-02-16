from dotenv import load_dotenv
import os
import json
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def verifier_agent(draft, research_notes):
    """
    Verify claims in the draft against research notes.
    Mark unsupported claims with "Not found in sources" flags.
    """
    notes_text = ""
    if isinstance(research_notes, list):
        for note in research_notes:
            if isinstance(note, dict):
                notes_text += f"Source: {note.get('citation', 'N/A')}\n{note.get('text', '')}\n\n"
            else:
                notes_text += f"{note}\n\n"
    else:
        notes_text = str(research_notes)
    
    draft_text = ""
    if isinstance(draft, dict):
        draft_text = json.dumps(draft, indent=2)
    else:
        draft_text = str(draft)
    
    prompt = f"""
    You are a Verifier Agent. Check claims in the draft against the research sources.
    
    RESEARCH SOURCES (ground truth):
    {notes_text}
    
    DRAFT TO VERIFY:
    {draft_text}
    
    Instructions:
    1. For each claim in the draft, check if it's supported by the research sources
    2. If a claim is NOT supported, mark it with [NOT FOUND IN SOURCES]
    3. If a claim is partially supported, mark it with [PARTIALLY SUPPORTED]
    4. If a claim contradicts sources, mark it with [CONTRADICTS SOURCES]
    5. Preserve all citations from the draft
    6. Return verified content in the same JSON format if applicable
    
    Return ONLY the verified version of the draft with annotations.
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    verified = response.choices[0].message.content
    
    #Ensure "Not found in sources" appears for unsupported claims
    if "[NOT FOUND IN SOURCES]" not in verified and "not found" not in verified.lower():
        #Check if any sources were actually used
        if "citation" not in verified.lower() and len(research_notes) == 0:
            verified = f"[NOT FOUND IN SOURCES]\n\nNo supporting research documents were available for this query.\n\n{verified}"
    
    return verified
