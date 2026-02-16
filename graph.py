from agents.planner_agent import planner_agent
from agents.research_agent import research_agent
from agents.writer_agent import writer_agent
from agents.verifier_agent import verifier_agent
import time
import json

def run_copilot(user_task):
    """
    Main orchestration function for the multi-agent copilot.
    Returns structured output with all required components.
    """
    trace_log = []
    obs_table = []

    #Step 1: Planner Decompose the task
    start = time.time()
    plan = planner_agent(user_task)
    planner_latency = time.time() - start
    trace_log.append({
        "agent": "Planner",
        "task": user_task,
        "output": plan,
        "latency_sec": planner_latency
    })
    obs_table.append({"agent": "Planner", "latency_sec": round(planner_latency, 2)})

    #Step 2: Research Retrieve grounded notes with citations
    start = time.time()
    notes = research_agent(user_task)  # Returns list of dicts with citations
    research_latency = time.time() - start
    trace_log.append({
        "agent": "Research",
        "task": plan,
        "output": notes,
        "latency_sec": research_latency
    })
    obs_table.append({"agent": "Research", "latency_sec": round(research_latency, 2)})

    #Step 3: Writer Produce structured deliverable (JSON)
    start = time.time()
    draft = writer_agent(notes)  #Returns dict with executive_summary, email, action_list
    writer_latency = time.time() - start
    trace_log.append({
        "agent": "Writer",
        "task": "Generate deliverable from research",
        "output": draft,
        "latency_sec": writer_latency
    })
    obs_table.append({"agent": "Writer", "latency_sec": round(writer_latency, 2)})

    #Step 4: Verifier Check for hallucinations and unsupported claims
    start = time.time()
    verified = verifier_agent(draft, notes)
    verifier_latency = time.time() - start
    trace_log.append({
        "agent": "Verifier",
        "task": "Verify claims against sources",
        "output": verified,
        "latency_sec": verifier_latency
    })
    obs_table.append({"agent": "Verifier", "latency_sec": round(verifier_latency, 2)})

    #Extract structured elements from verified output
    deliverable = {
        "executive_summary": "",
        "client_email": "",
        "action_list": [],
        "sources": [],
        "verified_content": verified
    }
    
    #Try to parse verified output if it contains JSON
    try:
        if isinstance(verified, str):
            if "```json" in verified:
                json_str = verified.split("```json")[1].split("```")[0].strip()
                parsed = json.loads(json_str)
                deliverable.update(parsed)
            elif isinstance(draft, dict):
                deliverable.update(draft)
    except:
        #If parsing fails, use draft structure if available
        if isinstance(draft, dict):
            deliverable.update(draft)

    #Extract sources from research notes
    sources_list = []
    if isinstance(notes, list):
        for note in notes:
            if isinstance(note, dict) and note.get("citation"):
                sources_list.append(note.get("citation"))
    deliverable["sources"] = list(set(sources_list))  #Remove duplicates

    return deliverable, trace_log, obs_table

#Run locally / CLI mode
if __name__ == "__main__":
    user_task = input("Enter your business task: ")
    deliverable, trace_log, obs_table = run_copilot(user_task)

    print("\n" + "="*60)
    print("EXECUTIVE SUMMARY")
    print("="*60)
    if isinstance(deliverable, dict):
        print(deliverable.get("executive_summary", deliverable.get("verified_content", "")))
    else:
        print(deliverable)

    print("\n" + "="*60)
    print("CLIENT EMAIL")
    print("="*60)
    if isinstance(deliverable, dict):
        print(deliverable.get("client_email", "Email not generated"))
    
    print("\n" + "="*60)
    print("ACTION LIST")
    print("="*60)
    if isinstance(deliverable, dict):
        for item in deliverable.get("action_list", []):
            print(f"  - {item.get('description', 'Task')}")
            print(f"    Owner: {item.get('owner', 'TBD')}, Due: {item.get('due_date', 'TBD')}, Confidence: {item.get('confidence', 'N/A')}")

    print("\n" + "="*60)
    print("SOURCES & CITATIONS")
    print("="*60)
    for source in deliverable.get("sources", []):
        print(f"  - {source}")

    print("\n" + "="*60)
    print("OBSERVABILITY TABLE")
    print("="*60)
    for obs in obs_table:
        print(f"  {obs['agent']}: {obs['latency_sec']}s")

    print("\n" + "="*60)
    print("FULL TRACE LOG")
    print("="*60)
    print(json.dumps(trace_log, indent=2))
