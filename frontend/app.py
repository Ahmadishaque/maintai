import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="MaintAI", page_icon="🛠️", layout="wide")
st.title("MaintAI")
st.caption("Policy-grounded maintenance intake assistant")

st.info(
    "The first milestone verifies that the frontend, backend, and PostgreSQL services "
    "can run together locally. LLM intake and policy retrieval will be added next."
)

if st.button("Check backend connection"):
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        response.raise_for_status()
        st.success("Backend is healthy.")
        st.json(response.json())
    except requests.RequestException as exc:
        st.error(f"Could not reach the backend: {exc}")
