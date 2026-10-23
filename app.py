import logging
import streamlit as st
from google import genai

logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="GOD'S PLAN AI",
    page_icon="🙏",
    layout="centered",
)

st.title("🙏 GOD'S PLAN AI")
st.write("Welcome, bro! Ask me anything.")
st.caption("Your personal AI chatbot 🤖")

# Check that the API key exists in Streamlit Secrets.
if "GEMINI_API_KEY" not in st.secrets:
    st.error(
        "API key not found. Please check "
        "GEMINI_API_KEY in Streamlit Secrets."
    )
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask me anything...")

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            client = genai.Client(
                api_key=st.secrets["GEMINI_API_KEY"]
            )

            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=question,
            )

            answer = response.text

            if not answer:
                answer = "I couldn't generate a reply. Please try again."

            st.markdown(answer)

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

        except Exception:
            logging.exception("Gemini API request failed")
            st.error(
                "I couldn't get a reply from Gemini. "
                "Please check the app logs."
            )
            
