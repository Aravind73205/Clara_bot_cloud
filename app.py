#import content
import os
import random
import json
import datetime
import hashlib
import streamlit as st
import traceback
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
    system_instruction=clara_prompt
)

def extract_message_data(message):
    """Safely extracts role and text content from either a dict or a Content object."""
    if isinstance(message, dict):
        # Handles custom dictionary-based history (the initial greeting)
        role = message.get("role")
        # Safely extract text from the dictionary structure
        content = message.get("parts", [{}])[0].get("text", "[Content Error]")
    else:
        # Handles the standard Content objects from the API's chat session history
        role = message.role
        # Safely extract text from the object structure
        content = message.parts[0].text if message.parts and message.parts[0].text else "[Reply loading...]"
    
    # Standardize the role for Streamlit
    display_role = "assistant" if role == "model" else role
    return display_role, content

def append_greeting():
    if not st.session_state.chat_session.history:  # Check if history is empty
        st.session_state.chat_session.history.append(
            {  # <-- FIX: Using the correct dictionary structure for history
                "role": "model",
                "parts": [
                    { "text": "Hi! I'm Clara, your AI health companion 😇. How are you feeling today?" }
                ]
            }
        )

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(
        history=[]  # <-- FIX: Start with an empty history
    )
    append_greeting()


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
    try:
        user_hash = hashlib.sha256(user_msg.encode()).hexdigest()[:12]
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_hash": user_hash,
            "user_length": len(user_msg),
            "ai_length": len(ai_msg),
            "model": "gemini-2.5-flash"
        }
        log_file = "/tmp/eval_logs.jsonl"  # for Cloud writing
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as log_err:
        print(f"Logging failed: {log_err}")
 
#user input fn
def user_input_msg(user_text):
    user_text = user_text.strip()

    # to get reply from gemini
    with st.spinner("Checking with Clara..."):
        try:
            response = st.session_state.chat_session.send_message(
                user_text,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7
                ),
            )     
            ai_reply = response.text
            log_interaction(user_text, ai_reply)

            st.success("Clara's got you! 💬")  # Quick feedback before refresh
            st.rerun()

        except Exception as e:
            tb = traceback.format_exc()
            st.error("Something went wrong")
            st.sidebar.text("Error:\n" + str(e))
            st.sidebar.text("Traceback:\n" + tb)

#homepage ui content
st.markdown("## 👩🏻‍⚕️ **Clara** |  Smart Health Assistant")

chat_container = st.container()
with chat_container:
    for message in st.session_state.chat_session.history:

        role, content = extract_message_data(message)

        if content:
            with st.chat_message(role):
                if role == "user":
                    st.markdown(f"**You:** {content}")
                else:
                    st.markdown(f"**Clara:** {style_response(content)}")

user_input = st.chat_input(placeholder="Ask Clara... 💬")
if user_input:
    user_input_msg(user_input)

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
    
    #clear button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_session = model.start_chat(
            history=[]
        )
        append_greeting()
        st.rerun()