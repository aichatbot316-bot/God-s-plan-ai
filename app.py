import streamlit as st
from google import genai

st.set_page_config(
    page_title="GOD'S PLAN AI",
    page_icon="🙏"
)

st.title("🙏 GOD'S PLAN AI")
st.write("Welcome, bro! Ask me anything.")

st.caption("Your personal AI chatbot 🤖")

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask me anything...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=question
            )

            answer = response.text or "Please try again."
            st.write(answer)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

    except Exception as e:
    st.error("Sorry bro! Something went wrong.")
    st.exception(e)
            
