import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
REQUESTS_URL = f"{BACKEND_URL}/api/v1/requests"

st.set_page_config(page_title="MaintAI", page_icon="🛠️", layout="wide")
st.title("MaintAI")
st.caption("Policy-grounded maintenance intake assistant")

with st.sidebar:
    st.subheader("System status")
    if st.button("Check backend connection", use_container_width=True):
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            response.raise_for_status()
            health = response.json()
            st.success("Backend is healthy.")
            st.json(health)
        except requests.RequestException as exc:
            st.error(f"Could not reach the backend: {exc}")

new_request_tab, history_tab = st.tabs(["New request", "Request history"])

with new_request_tab:
    st.subheader("Describe the maintenance issue")
    st.write(
        "Enter the issue in natural language. This milestone stores the original request; "
        "the next milestone will add Gemini-based structured extraction."
    )

    with st.form("maintenance_request_form", clear_on_submit=True):
        reporter_name = st.text_input("Reporter name", placeholder="Jordan Lee")
        location = st.text_input("Location", placeholder="Building 3, second floor")
        raw_description = st.text_area(
            "Issue description",
            height=180,
            placeholder=(
                "The air-conditioning unit is making a grinding noise and water is pooling "
                "underneath it. The issue started this morning."
            ),
        )
        submitted = st.form_submit_button("Create maintenance request", use_container_width=True)

    if submitted:
        payload = {
            "raw_description": raw_description,
            "reporter_name": reporter_name or None,
            "location": location or None,
        }
        try:
            response = requests.post(REQUESTS_URL, json=payload, timeout=10)
            response.raise_for_status()
            request_record = response.json()
            st.success(f"Request #{request_record['id']} was created.")
            st.json(request_record)
        except requests.HTTPError:
            detail = response.json().get("detail", response.text)
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
                        st.write(record["raw_description"])
                        st.caption(
                            f"Reporter: {record.get('reporter_name') or 'Not provided'} | "
                            f"Created: {record['created_at']}"
                        )
        except requests.RequestException as exc:
            st.error(f"Could not load request history: {exc}")
