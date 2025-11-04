#import content
import random
import streamlit as st
import google.generativeai as genai

#page config
st.set_page_config(
    page_title="MediBot - Your Health Assistant",
    layout="centered",
    initial_sidebar_state="expanded"
)

#api key load
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)

except KeyError:
    st.stop()

#prompt for clara
clara_prompt = f"""You are Mrs.Clara, an experienced AI powered family doctor, Your goal is to understand patient issues and support them.

Key Notes:
 Do not prescribe drugs or specific treatments beyond basic first aid
 If user Asked to generate Images(eg: show the image of how that allergy looks like), refuse politely.
 Flag sensitive topics (eg: if "suicide", "self-harm", "abuse", "violence", etc.), "Escalate: Advise immediate professional help."
 At the end of the chat:
  Summarize the coversation in 3-5 bullet points. 
  Ask: "Did this help? (Yes/No)" and suggest next steps.

 You are not a replacement for inperson care, always guide toward professional consulting when needed.
"""

#model init
model_name = "gemini-2.5-flash"
model = genai.GenerativeModel(
    model_name=model_name,
    system_instruction=clara_prompt,
    generation_config={"temperature": 0.3, "top_p": 0.9, "max_output_tokens": 1024}
)

#session state init
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])


#default msg, if no msg sent yet
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "text": "Hi! I'm Clara, your AI health companion 😇. How are you feeling today?"}
    ]

#custom response
def style_response(text):
    starters = ["Hmm", "Okay", "Alright,"]
    emojis = ["💊","👍","😊"]

    if random.random() < 0.2:
        text = random.choice(starters) + " " + text

    if random.random() < 0.4:
        text += " " + random.choice(emojis)

    return text

#chat interface
st.markdown("## 👩🏻‍⚕️ **Clara** | Smart Health Assistant")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["text"])

#user input handling
if user_input := st.chat_input("Ask Clara... 💬"):
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "text": user_input})

    placeholder = st.empty()

    # to get reply from gemini
    with st.spinner("Clara is thinking..."):
        try:
            response = st.session_state.chat_session.send_message(user_input)
            ai_reply = style_response(response.text.strip())

            with placeholder.container():
                with st.chat_message("assistant"):
                    st.markdown(ai_reply)

            st.session_state.messages.append({"role": "assistant", "text": ai_reply})

        except Exception:
            placeholder.error("⚠️ Something went wrong while Clara was thinking.")

#sidebar for guidance
with st.sidebar:

    st.markdown("---")
    st.markdown("### 🔹 **Quick Tips**")

    st.markdown("""
    - **Describe your symptoms** ( severity, duration, etc...)
    - **Ask about health tips** (Healthy Snacks, Fatfree Foods..)
    - **Need urgent help?** 🚨 Contact Professional!
    """)
    
    st.markdown("---")
    st.markdown("### ⚠️ **Note**")

    st.markdown("""
    -  I’m your **Smart health Assistant, not a certified doctor**, consult a professional for serious concerns🌱
    """)
    

    st.markdown("---")
    st.markdown("♊️ *Powered by Google's Gemini*")
    
    
    st.markdown("---")
    #clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_session = model.start_chat(
            history=[]
        )
        st.session_state.messages = [
            {"role": "assistant", "text": "Hi! I'm Clara, your AI health companion 😇. How are you feeling today?"}
        ]
        st.rerun()