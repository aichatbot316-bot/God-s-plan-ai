import logging
import streamlit as st
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="GOD'S PLAN AI",
    page_icon="🙏",
    layout="centered",
)

st.title("🙏 GOD'S PLAN AI")
st.write("Welcome, bro! Ask me anything.")
st.caption("Your personal AI chatbot 🤖📸")

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

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("image_bytes"):
            st.image(
                message["image_bytes"],
                caption="Uploaded photo",
                use_container_width=True,
            )

        st.markdown(message["content"])

# Photo upload options
st.subheader("📸 Ask about a photo")

uploaded_image = st.file_uploader(
    "Choose a photo from your gallery",
    type=["jpg", "jpeg", "png", "webp"],
    key="gallery_image",
)

camera_image = st.camera_input(
    "Or take a new photo",
    key="camera_image",
)

# Prefer the camera photo when one is available
selected_image = camera_image or uploaded_image

image_bytes = None
mime_type = None

if selected_image is not None:
    image_bytes = selected_image.getvalue()
    mime_type = selected_image.type or "image/jpeg"

    if len(image_bytes) > 10 * 1024 * 1024:
        st.warning("Please choose a photo smaller than 10 MB.")
        image_bytes = None
        mime_type = None
    else:
        st.image(
            image_bytes,
            caption="Photo ready to send",
            use_container_width=True,
        )

# Chat input
question = st.chat_input(
    "Ask a question or ask about your photo..."
)

if question:
    # Save user's message
    user_message = {
        "role": "user",
        "content": question,
        "image_bytes": image_bytes,
        "mime_type": mime_type,
    }

    st.session_state.messages.append(user_message)

    with st.chat_message("user"):
        if image_bytes:
            st.image(
                image_bytes,
                caption="Uploaded photo",
                use_container_width=True,
            )

        st.markdown(question)

    # Generate response
    with st.chat_message("assistant"):
        reply_box = st.empty()
        answer_parts = []

        try:
            # Prepare text and optional image
            contents = [question]

            if image_bytes and mime_type:
                image_part = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type,
                )
                contents.append(image_part)

            # Stream the response from Gemini
            stream = client.models.generate_content_stream(
                model="gemini-3.8-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are GOD'S PLAN AI, a helpful AI assistant. "
                        "Answer clearly and respectfully. "
                        "When an image is provided, examine it carefully "
                        "and answer the user's question about it. "
                        "Keep answers concise unless the user requests "
                        "a detailed explanation. If something in an "
                        "image is unclear, say so honestly."
                    ),
                    max_output_tokens=512,
                ),
            )

            for chunk in stream:
                if chunk.text:
                    answer_parts.append(chunk.text)
                    reply_box.markdown(
                        "".join(answer_parts) + " ▌"
                    )

            answer = "".join(answer_parts).strip()

            if not answer:
                answer = (
                    "Sorry bro, I couldn't generate a reply. "
                    "Please try again."
                )

            reply_box.markdown(answer)

            # Save assistant response
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

        except Exception:
            logger.exception("Gemini request failed")
            reply_box.error(
                "Sorry bro! Something went wrong. "
                "Please try again or check the app logs."
            )

# Clear conversation
if st.session_state.messages:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()         
