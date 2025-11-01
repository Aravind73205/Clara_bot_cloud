#import content
from dotenv import load_dotenv
import os
import random
import json
import datetime
import hashlib
import streamlit as st
import google.generativeai as genai

#api key load
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
if not os.getenv("GOOGLE_API_KEY"):
    st.stop()

#gemini client initialize
try:
    gemini = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"error occured:{e}")
    st.stop()

#page config
st.set_page_config(
    page_title="MediBot - Your Health Assistant",
    layout="centered",
    initial_sidebar_state="expanded"
)

#page default msg
Welcome_msg = {
    "role": "assistant",
    "content": "Hi! I'm Clara, your AI health companion 😇. How are you feeling today?"
}

st.session_state.setdefault("messages", [Welcome_msg])

#custom response
def style_response(text):
    starters = ["Hmm", "Okay", "Alright,"]
    emojis = ["💊","👍","😊"]

    if random.random() < 0.2:
        text = random.choice(starters) + " " + text

    if random.random() < 0.4:
        text += " " + random.choice(emojis)

    return text

#log tracking fn
def log_interaction(user_msg, ai_msg):
    user_hash = hashlib.sha256(user_msg.encode()).hexdigest()[:12]
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "user_hash": user_hash,
        "user_length": len(user_msg),
        "ai_length": len(ai_msg),
        "model": "gemini-1.5-flash"
    }
    with open("eval_logs.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
 
#user input fn
def user_input_msg():
    user_text = st.session_state.input_field.strip()

    st.session_state.messages.append({"role": "user", "content": user_text})
    
    #to store chat history
    recent_chat = st.session_state.messages[-20:]
    chat_prompt = "\n".join([f"{msg['role'].title()}: {msg['content']}" for msg in recent_chat])
    
    #prompt for clara
    clara_prompt = f"""You are Mrs.Clara, an experienced AI powered family doctor, Your goal is to understand patient issues and support them.

Important Instructions:
 Do not prescribe drugs or specific treatments beyond basic first aid
 At the end of the chat:
  Send them key points of the Conversation(like summary)
  And Ask them did i solve your issue?

 You are not a replacement for inperson care, always guide toward professional consulting when needed.

Chat history:
{chat_prompt}

Your response:"""
    
model = genai.GenerativeModel("gemini-1.5-flash")
    #to get reply from gemini
with st.spinner("Checking with Clara..."):
    try:
        response = model.generate_content(clara_prompt)
        ai_reply = response.text
        friendly_reply = style_response(ai_reply)
            
        log_interaction(user_text, ai_reply)
        st.session_state.messages.append({"role": "assistant", "content": friendly_reply})

    except Exception as error:
        st.error(f"something went wrong: {error}")

        st.session_state.input_field = ""


#homepage ui content
st.markdown("## 👩🏻‍⚕️ **Clara** |  Smart Health Assistant")

chat_container = st.container()
with chat_container:
    for message in st.session_state.messages[-50:]:
        content = message["content"]
        role = message["role"]
        with st.chat_message(role):
            if role == "user":
                st.markdown(f"**You:** {content}")
            else:
                st.markdown(f"**Clara:** {content}")

user_input = st.chat_input(placeholder="Ask Clara... 💬")
if user_input:
    st.session_state.input_field = user_input
    user_input_msg()
    st.rerun()

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
    -  I'm your **Smart health Assistant, not a certified doctor**, consult a professional for serious concerns🌱
    """)
    

    st.markdown("---")
    st.markdown("♊️ *Powered by Google's Gemini*")
    
    #for clear chat
    st.markdown("---")
    if st.button("🗑️ **Clear Chat**", use_container_width=True):
        st.session_state.messages = [Welcome_msg]
        if "input_field" in st.session_state:
            st.session_state.input_field = ""
        st.rerun()