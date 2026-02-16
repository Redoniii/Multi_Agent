from dotenv import load_dotenv
import os
from openai import OpenAI
from retrieval.vector_store import retrieve

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SIMILARITY_THRESHOLD = 0.5  # L2 distance threshold (stricter: reject off-topic queries)

def research_agent(task):
    """
    Research agent retrieves documents and creates grounded notes with citations.
    Returns list of dicts with 'text', 'citation', and 'supported' fields.
    """
    results = retrieve(task, k=3)
    
    if not results:
        return [{"text": "No relevant documents found in knowledge base.", "citation": "N/A", "supported": False}]
    
    #Accept if best match score < threshold
    best_score = min(r.get("similarity_score", float('inf')) for r in results)
    
    if best_score > SIMILARITY_THRESHOLD:
        return [{
            "text": f"Query appears to be outside the domain of available supply chain documents. Best relevance score: {best_score:.3f} (threshold: {SIMILARITY_THRESHOLD}).",
            "citation": "N/A",
            "supported": False,
            "reason": "Low relevance - out of domain"
        }]
    
    notes = []
    for result in results:
        if result.get("supported") == False and result.get("text") == "No relevant documents found.":
            notes.append(result)
            continue
        
        #Create research note with citation
        note = {
            "text": result.get("text", "")[:500],  #Limit text length for notes
            "citation": result.get("citation", "N/A"),
            "doc_name": result.get("doc_name", "unknown"),
            "similarity_score": result.get("similarity_score", 0),
            "supported": result.get("supported", True)
        }
        notes.append(note)
    
    return notes
