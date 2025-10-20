import os
import time
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# ---------- Setup ----------
load_dotenv()  # load .env if present
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ASSISTANT_ID = os.getenv("ASSISTANT_ID", "asst_PyDQj8hOe83PXXdZ2efqsmoS")

if not OPENAI_API_KEY:
    st.error("Missing OPENAI_API_KEY. Set it in .env or Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

st.set_page_config(page_title="Grade 7 Science Tutor", page_icon="🧪", layout="centered")
st.title("🧪 Grade 7 Science Tutor")
st.caption("Ask science questions. The tutor teaches with examples → explanation → practice → feedback.")

# ---------- Session state ----------
if "thread_id" not in st.session_state:
    # Each browser session gets its own conversation Thread
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- UI: chat history ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- User input ----------
user_input = st.chat_input("Ask a Grade 7 science question (e.g., 'Why does iron rust faster near the sea?')")

def run_assistant_and_stream(thread_id: str, assistant_id: str) -> str:
    """
    Creates a Run on the thread and streams tokens into the UI as they arrive.
    Returns the final full text.
    """
    # Start the run
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

    # Stream status polling (simple + reliable)
    placeholder = st.empty()
    collected_text = ""

    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        status = run.status

        if status in ("queued", "in_progress"):
            # Fetch newest messages so far (the assistant may have partial content if tools run)
            messages = client.beta.threads.messages.list(thread_id=thread_id, order="desc", limit=1).data
            if messages and messages[0].role == "assistant":
                parts = messages[0].content
                if parts and hasattr(parts[0], "text") and parts[0].text:
                    collected_text = parts[0].text.value
                    placeholder.markdown(collected_text)
            time.sleep(0.6)
            continue

        elif status == "requires_action":
            # If you add custom tools/functions later, handle them here.
            placeholder.info("Assistant requested an action (tool call). No custom tools configured yet.")
            time.sleep(0.6)
            continue

        elif status in ("completed", "failed", "cancelled", "expired"):
            # Get final assistant message
            messages = client.beta.threads.messages.list(thread_id=thread_id, order="desc", limit=1).data
            if messages and messages[0].role == "assistant":
                parts = messages[0].content
                if parts and hasattr(parts[0], "text") and parts[0].text:
                    collected_text = parts[0].text.value
            if status != "completed":
                placeholder.error(f"Run ended with status: {status}")
            else:
                placeholder.empty()
            return collected_text

        else:
            placeholder.warning(f"Unknown status: {status}")
            time.sleep(0.6)

if user_input:
    # 1) Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2) Add user message to the Thread
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=user_input
    )

    # 3) Create a placeholder for assistant response
    with st.chat_message("assistant"):
        final_text = run_assistant_and_stream(
            thread_id=st.session_state.thread_id,
            assistant_id=ASSISTANT_ID
        )
        st.markdown(final_text)

    # 4) Save to local chat history
    st.session_state.messages.append({"role": "assistant", "content": final_text})

# ---------- Sidebar: info ----------
with st.sidebar:
    st.subheader("Configuration")
    st.write("**Assistant ID**")
    st.code(ASSISTANT_ID)
    st.write("**Thread ID**")
    st.code(st.session_state.thread_id)
    st.markdown("""
**Tips**
- Your Assistant already has **File Search** enabled, so it will use the vector store you attached in the dashboard.
- To let it do math/plots, enable **Code Interpreter** on the dashboard.
- To call your own APIs (simulations, LMS, etc.), add **Functions** on the dashboard and handle `requires_action` in `app.py`.
    """)
