import logging
import streamlit as st
from google import genai

# Log errors without exposing secrets to users.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="GOD'S PLAN AI",
    page_icon="🙏",
    layout="centered",
)

# App heading
st.title("🙏 GOD'S PLAN AI")
st.write("Welcome, bro! Ask me anything.")
st.caption("Your personal AI chatbot 🤖")

# Check API key
if "GEMINI_API_KEY" not in st.secrets:
    st.error(
        "Gemini API key not found. "
        "Please check GEMINI_API_KEY in Streamlit Secrets."
    )
    st.stop()

# Create Gemini client
client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

# Store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
question = st.chat_input("Ask GOD'S PLAN AI anything...")

if question:
    # Show and save the user's message
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    # Generate a streaming response
    with st.chat_message("assistant"):
        answer_parts = []
        reply_box = st.empty()

        try:
            stream = client.models.generate_content_stream(
                model="gemini-3.8-flash",
                contents=question,
            )

            for chunk in stream:
                if chunk.text:
                    answer_parts.append(chunk.text)
                    reply_box.markdown("".join(answer_parts))

            answer = "".join(answer_parts).strip()

            if not answer:
                answer = (
                    "Sorry bro, I couldn't generate a reply. "
                    "Please try asking in a different way."
                )
                reply_box.markdown(answer)

            # Save the complete answer
            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

        except Exception:
            logger.exception("Gemini response generation failed")
            reply_box.error(
                "Sorry bro! I couldn't get a reply from Gemini. "
                "Please try again in a little while."
            )

# Clear chat history
if st.session_state.messages:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
