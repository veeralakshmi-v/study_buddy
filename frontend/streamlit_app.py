"""
streamlit_app.py

AI Study Buddy - Streamlit frontend

This file provides a redesigned Streamlit interface for the AI Study Buddy demo.
Features:
- Sidebar settings: editable API URL, model selector (placeholder), temperature slider.
- Upload supporting text files (TXT/MD) and include them in requests using "Send + context".
- Conversation history with simple, readable display.

Usage
-----
1. Start the backend FastAPI server (default localhost:8000) and ensure it exposes POST /chat
    returning JSON with an `answer` (or `response`) field.
2. Run this app:
    cd ".../frontend"
    streamlit run streamlit_app.py

Notes
-----
- The frontend will send JSON with keys: question, model, temperature, and optional context
  (list of file contents) when using the Send + context button.
- API URL is editable in the sidebar. Adjust if your backend runs elsewhere.

Changelog:
- 2025-10-15: Reworked UI: sidebar, file uploader, Send + context button, clearer layout.
"""

import streamlit as st
import requests
from textwrap import shorten

API_URL = "http://localhost:8000"

if "history" not in st.session_state:
    st.session_state.history = []  # list of (role, text)

if "context_files" not in st.session_state:
    st.session_state.context_files = []

# Sidebar: settings and utilities
with st.sidebar:
    st.header("Settings")
    api_url = st.text_input("API URL", value=API_URL)
    model = st.selectbox("Model", options=["default"], index=0, help="Backend model selector (placeholder)")
    temp = st.slider("Creativity (temperature)", 0.0, 1.0, 0.2, 0.05)
    st.divider()
    st.header("Context")
    uploaded = st.file_uploader("Upload supporting text files (optional)", accept_multiple_files=True, type=["txt", "md"])
    if uploaded:
        # store simple filename+content for preview and possible use
        st.session_state.context_files = []
        for f in uploaded:
            try:
                content = f.read().decode("utf-8")
            except Exception:
                content = "<binary or unreadable file>"
            st.session_state.context_files.append({"name": f.name, "content": content})
        st.success(f"Loaded {len(uploaded)} file(s)")
    if st.button("Clear context"):
        st.session_state.context_files = []

    st.divider()
    if st.button("Clear conversation"):
        st.session_state.history = []
        st.rerun()

# Main layout: two columns - chat and help/reference
chat_col, info_col = st.columns([3, 1])

with chat_col:
    st.markdown("# 🎓 AI Study Buddy")
    st.markdown("Ask questions about your study material and get concise explanations.")

    # conversation area
    box = st.container()
    with box:
        for role, text in st.session_state.history:
            if role == "user":
                st.markdown(f"**You:** {shorten(text, width=500)}")
            else:
                st.markdown(f"**Assistant:** {shorten(text, width=500)}")

    # input
    with st.form(key="input_form", clear_on_submit=True):
        prompt = st.text_area("Your question", placeholder="e.g. Explain gradient descent in simple terms", height=120)
        cols = st.columns([1, 1, 1])
        with cols[0]:
            send = st.form_submit_button("Send")
        with cols[1]:
            send_with_context = st.form_submit_button("Send + context")
        with cols[2]:
            cancel = st.form_submit_button("Cancel")

    if cancel:
        st.info("Message cancelled")

    if (send or send_with_context) and prompt.strip():
        st.session_state.history.append(("user", prompt))
        payload = {"question": prompt, "model": model, "temperature": temp}
        # attach context content if requested
        if send_with_context and st.session_state.context_files:
            payload["context"] = [c["content"] for c in st.session_state.context_files]

        with st.spinner("Thinking..."):
            try:
                resp = requests.post(f"{api_url}/chat", json=payload, timeout=30)
                resp.raise_for_status()
                answer = resp.json().get("answer") or resp.json().get("response") or "(no answer)"
                st.session_state.history.append(("assistant", answer))
            except Exception as e:
                st.session_state.history.append(("assistant", f"⚠️ Error: {e}"))

        # Scroll to bottom by rerunning (Streamlit re-renders showing latest history)
        st.rerun()

with info_col:
    st.markdown("### Tips")
    st.markdown("- Provide focused questions for best results.\n- Use 'Send + context' to include uploaded files.\n- Clear conversation from the sidebar.")
    if st.session_state.context_files:
        st.markdown("---")
        st.markdown("### Uploaded context preview")
        for f in st.session_state.context_files:
            st.markdown(f"**{f['name']}**")
            st.code(shorten(f['content'], width=400))

