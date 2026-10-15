import streamlit as st
import requests

API_URL = "http://localhost:8000/api"

st.set_page_config(page_title="LeadScout AI Agent", page_icon="🎯", layout="wide")

st.title("🎯 LeadScout — B2B Lead Research & Outreach Agent")
st.caption("Powered by LangGraph, Gemini, and Tavily Search")

# Sidebar - Input Lead Details
st.sidebar.header("Prospect Details")
domain = st.sidebar.text_input("Company Domain", value="databricks.com")
contact_name = st.sidebar.text_input("Contact Name", value="Alex Rivera")
contact_role = st.sidebar.text_input("Role", value="VP of Engineering")
offering = st.sidebar.text_input("Your Product Offering", value="LLM Observability Platform")

if st.sidebar.button("🚀 Start Lead Research", type="primary"):
    with st.spinner("Agent researching company and drafting outreach..."):
        payload = {
            "company_domain": domain,
            "contact_name": contact_name,
            "contact_role": contact_role,
            "target_offering": offering
        }
        try:
            res = requests.post(f"{API_URL}/leads/start", json=payload)
            if res.status_code == 200:
                st.session_state["data"] = res.json()
                st.success("Workflow started successfully!")
            else:
                st.error(f"Failed to start workflow. Server error: {res.text}")
        except Exception as e:
            st.error(f"Could not connect to FastAPI backend: {str(e)}")

# Display Results
if "data" in st.session_state:
    data = st.session_state["data"]
    state = data.get("state", {})
    thread_id = data.get("thread_id")

    st.subheader(f"Thread ID: `{thread_id}`")

    # Display Extracted Intelligence
    analysis = state.get("company_analysis")
    if analysis:
        st.markdown("### 🏢 Company Intelligence")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Company:** {analysis.get('company_name', 'N/A')}")
            st.markdown(f"**Industry:** {analysis.get('industry', 'N/A')}")
            st.info(analysis.get('summary', 'No summary available.'))
        with col2:
            st.markdown("**Key Triggers:**")
            triggers = analysis.get("value_proposition_triggers", [])
            if triggers:
                for t in triggers:
                    st.write(f"- {t}")
            else:
                st.write("No specific triggers extracted.")

    # Display Generated Draft & Human Review Box
    draft = state.get("email_draft")
    is_waiting = data.get("is_waiting_for_approval")

    if draft and is_waiting:
        st.warning("⏸️ Agent Execution Paused for Human Approval")

        st.markdown("### ✉️ Generated Cold Email Draft")
        st.text_input("Subject Line", value=draft.get("subject_line", ""), key="subj")
        st.text_area("Email Body", value=draft.get("body", ""), height=200, key="body_display")
        st.text_input("Call to Action", value=draft.get("call_to_action", ""), key="cta")

        feedback = st.text_input("Feedback for Re-drafting (optional if requesting revisions)", key="fb")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("✅ Approve & Send", type="primary"):
                with st.spinner("Logging outreach to CRM..."):
                    res = requests.post(
                        f"{API_URL}/leads/resume",
                        json={"thread_id": thread_id, "status": "approved", "feedback": ""}
                    )
                    if res.status_code == 200:
                        st.session_state["data"] = res.json()
                        st.success("Email approved and logged!")
                        st.rerun()
                    else:
                        st.error("Failed to approve draft.")

        with col_b:
            if st.button("🔄 Request Revision"):
                if not feedback:
                    st.warning("Please enter feedback explaining what changes are needed.")
                else:
                    with st.spinner("Agent re-drafting email based on feedback..."):
                        res = requests.post(
                            f"{API_URL}/leads/resume",
                            json={"thread_id": thread_id, "status": "edit_requested", "feedback": feedback}
                        )
                        if res.status_code == 200:
                            st.session_state["data"] = res.json()
                            st.success("Revision requested. New draft generated!")
                            st.rerun()
                        else:
                            st.error("Failed to request revision.")

        with col_c:
            if st.button("❌ Reject Draft"):
                with st.spinner("Terminating workflow..."):
                    res = requests.post(
                        f"{API_URL}/leads/resume",
                        json={"thread_id": thread_id, "status": "rejected", "feedback": ""}
                    )
                    if res.status_code == 200:
                        st.session_state["data"] = res.json()
                        st.warning("Draft rejected. Workflow terminated.")
                        st.rerun()
                    else:
                        st.error("Failed to reject draft.")

    elif state.get("approval_status") == "approved":
        st.success("🎉 Email approved and logged successfully in CRM database!")
    elif state.get("approval_status") == "rejected":
        st.error("❌ Workflow was terminated (Draft Rejected).")