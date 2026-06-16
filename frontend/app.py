import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
REQUESTS_URL = f"{BACKEND_URL}/api/v1/requests"


def render_triage(record: dict[str, object]) -> None:
    """Render the structured triage result and operational metadata."""
    data = record.get("structured_data") or {}
    metadata = record.get("llm_metadata") or {}
    if not isinstance(data, dict) or not isinstance(metadata, dict):
        st.json(record)
        return

    status_value = str(record.get("status", "unknown"))
    if status_value == "needs_review":
        st.warning("Human review required")
    else:
        st.success("Automated triage completed")

    st.subheader(str(data.get("summary", "Maintenance request")))
    metric_columns = st.columns(4)
    metric_columns[0].metric("Category", str(data.get("issue_category", "unknown")))
    metric_columns[1].metric("Severity", str(data.get("severity", "unknown")))
    metric_columns[2].metric("Equipment", str(data.get("equipment_type") or "unknown"))
    confidence = data.get("confidence")
    confidence_label = f"{float(confidence):.0%}" if isinstance(confidence, int | float) else "n/a"
    metric_columns[3].metric("Confidence", confidence_label)

    left_column, right_column = st.columns(2)
    with left_column:
        st.markdown("#### Observed symptoms")
        symptoms = data.get("symptoms") or []
        if symptoms:
            for symptom in symptoms:
                st.write(f"- {symptom}")
        else:
            st.write("No symptoms extracted.")

        st.markdown("#### Recommended actions")
        actions = data.get("recommended_actions") or []
        if actions:
            for action in actions:
                st.write(f"- {action}")
        else:
            st.write("Await human review.")

    with right_column:
        st.markdown("#### Missing information")
        missing = data.get("missing_information") or []
        if missing:
            for item in missing:
                st.write(f"- {item}")
        else:
            st.write("No critical gaps identified.")

        st.markdown("#### Policy evidence")
        citations = data.get("policy_citations") or []
        if citations:
            for citation in citations:
                st.code(str(citation))
        else:
            st.write("No validated policy citation was returned.")

    with st.expander("LLM usage and audit metadata"):
        st.json(metadata)


st.set_page_config(page_title="MaintAI", page_icon="🛠️", layout="wide")
st.title("MaintAI")
st.caption("Policy-grounded maintenance intake assistant")

with st.sidebar:
    st.subheader("System status")
    if st.button("Check backend connection", use_container_width=True):
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            response.raise_for_status()
            st.success("Backend and database are healthy.")
            st.json(response.json())
        except requests.RequestException as exc:
            st.error(f"Could not reach the backend: {exc}")

    st.divider()
    st.caption("One Gemini call performs structured extraction and policy-grounded triage.")

new_request_tab, history_tab = st.tabs(["New request", "Request history"])

with new_request_tab:
    st.subheader("Describe the maintenance issue")
    st.write(
        "MaintAI retrieves relevant internal procedures, calls Gemini for schema-constrained "
        "extraction, validates citations, and stores the complete audit record in PostgreSQL."
    )

    with st.form("maintenance_request_form", clear_on_submit=True):
        reporter_name = st.text_input("Reporter name", placeholder="Jordan Lee")
        location = st.text_input("Location", placeholder="Building 3, mechanical room")
        raw_description = st.text_area(
            "Issue description",
            height=180,
            placeholder=(
                "The cooling pump is vibrating heavily and leaking dark fluid near the rear "
                "seal. The issue started this morning."
            ),
        )
        submitted = st.form_submit_button("Analyze and create request", use_container_width=True)

    if submitted:
        payload = {
            "raw_description": raw_description,
            "reporter_name": reporter_name or None,
            "location": location or None,
        }
        try:
            with st.spinner("Retrieving policies and analyzing the request..."):
                response = requests.post(REQUESTS_URL, json=payload, timeout=60)
            response.raise_for_status()
            request_record = response.json()
            st.success(f"Request #{request_record['id']} was created.")
            render_triage(request_record)
        except requests.HTTPError:
            try:
                detail = response.json().get("detail", response.text)
            except ValueError:
                detail = response.text
            st.error(f"The request could not be created: {detail}")
        except requests.RequestException as exc:
            st.error(f"Could not reach the backend: {exc}")

with history_tab:
    st.subheader("Recent maintenance requests")
    if st.button("Refresh request history", use_container_width=True):
        try:
            response = requests.get(REQUESTS_URL, params={"limit": 25}, timeout=10)
            response.raise_for_status()
            records = response.json()
            if not records:
                st.info("No maintenance requests have been created yet.")
            else:
                for record in records:
                    with st.expander(
                        f"Request #{record['id']} · {record['status']} · "
                        f"{record.get('location') or 'Location not provided'}"
                    ):
                        st.caption(
                            f"Reporter: {record.get('reporter_name') or 'Not provided'} | "
                            f"Created: {record['created_at']}"
                        )
                        render_triage(record)
        except requests.RequestException as exc:
            st.error(f"Could not load request history: {exc}")
