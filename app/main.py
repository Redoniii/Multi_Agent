import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from graph import run_copilot


st.set_page_config(page_title="Enterprise Multi-Agent Copilot", layout="wide")
st.title("🤖 Enterprise Multi-Agent Copilot – Supply Chain")
st.markdown("Transform supply chain business requests into structured, decision-ready deliverables using AI agents grounded in supply chain management documents and best practices.")

#Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    st.info("This system uses 4 coordinated agents to deliver comprehensive analysis with full citations.")

#Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 Your Business Task")
    user_task = st.text_area("Enter your business task or question:", height=100, 
                             placeholder="Example: What are best practices for supply chain resilience and coordination?")

with col2:
    st.subheader("📊 Quick Info")
    st.metric("Agents", "4", "Plan → Research → Draft → Verify")
    st.metric("Documents", "8", "Supply Chain Management")
    st.metric("Citations", "Full Tracking", "Document + Chunk ID")

#Run system
if st.button("🚀 Run Multi-Agent Workflow", use_container_width=True, type="primary"):
    if not user_task.strip():
        st.error("Please enter a business task.")
    else:
        with st.spinner("🔄 Running multi-agent workflow..."):
            try:
                deliverable, trace_log, obs_table = run_copilot(user_task)
                
                # Store results in session for display
                st.session_state.deliverable = deliverable
                st.session_state.trace_log = trace_log
                st.session_state.obs_table = obs_table
                
            except Exception as e:
                st.error(f"❌ Error during execution: {str(e)}")
                st.info("Make sure your OPENAI_API_KEY is set in .env file")

#Display results if available
if "deliverable" in st.session_state:
    deliverable = st.session_state.deliverable
    
    #Tabs for different output views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📄 Executive Summary", "📧 Email", "✅ Action Items", "📚 Sources", "🔍 Full Trace"]
    )
    
    with tab1:
        st.subheader("Executive Summary")
        summary = deliverable.get("executive_summary", "Summary not available")
        st.write(summary)
    
    with tab2:
        st.subheader("Client Email")
        email = deliverable.get("client_email", "Email not available")
        st.text(email)
    
    with tab3:
        st.subheader("Action Items")
        action_list = deliverable.get("action_list", [])
        if action_list:
            for i, item in enumerate(action_list, 1):
                st.markdown(f"**Task {i}: {item.get('description', 'N/A')}**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Owner", item.get("owner", "TBD"))
                with col2:
                    st.metric("Confidence", item.get("confidence", "N/A"))
                with col3:
                    st.metric("Due Date", item.get("due_date", "TBD"))
                st.divider()
        else:
            st.info("No action items generated.")
    
    with tab4:
        st.subheader("Sources & Citations")
        sources = deliverable.get("sources", [])
        if sources:
            for i, source in enumerate(sources, 1):
                st.write(f"{i}. `{source}`")
        else:
            st.warning("No sources cited. This may indicate [NOT FOUND IN SOURCES]")
    
    with tab5:
        st.subheader("Complete Workflow Trace")
        
        #Observability table
        st.markdown("**Observability Metrics**")
        obs_data = []
        for obs in st.session_state.obs_table:
            obs_data.append({
                "Agent": obs["agent"],
                "Latency (sec)": obs["latency_sec"]
            })
        st.dataframe(obs_data, use_container_width=True)
        
        #Full trace log
        st.markdown("**Detailed Trace Log**")
        for log in st.session_state.trace_log:
            with st.expander(f"🔔 {log['agent']} Agent"):
                task_text = str(log.get('task', 'N/A'))[:200]
                st.write(f"**Task:** {task_text}...")
                latency = log.get('latency_sec', 0)
                if isinstance(latency, (int, float)):
                    st.write(f"**Latency:** {latency:.2f}s")
                else:
                    st.write(f"**Latency:** {latency}")
                st.write(f"**Output (first 500 chars):**")
                output_text = str(log.get('output', 'No output'))[:500]
                st.code(output_text)

#Footer
st.divider()
st.markdown("""
---
**Multi-Agent System Architecture:**
1. 🗂️ **Planner** - Decomposes your task into subtasks
2. 🔎 **Researcher** - Retrieves grounded evidence with citations  
3. ✍️ **Writer** - Creates structured deliverable (executive summary + email + actions)
4. ✔️ **Verifier** - Blocks unsupported claims & finds contradictions
""")
