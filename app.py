import streamlit as st
from google import genai

st.set_page_config(page_title="RAGHU AI", page_icon="🤖")

st.title("🤖 RAGHU AI")
st.write("Welcome, bro! Ask me anything. ❤️")

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

question = st.chat_input("Ask RAGHU AI anything...")

if question:
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=question
                )
                st.write(response.text)
            except Exception:
                st.error("Sorry bro! Something went wrong.")
