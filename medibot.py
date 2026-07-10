import streamlit as st
from groq import Groq

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="MediBot",
    page_icon="🩺",
    layout="centered"
)

# =========================
# GROQ SETUP
# =========================
import streamlit as st
from groq import Groq

client = Groq(api_key=st.secrets["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"])
# =========================
# SYSTEM PROMPT
# =========================
SYSTEM_PROMPT = """
You are MediBot, an educational health assistant.

Rules:
- You are not a licensed doctor.
- Never provide a definitive diagnosis.
- Ask only one question at a time.
- Be empathetic and professional.
- Always gather information in this order: Name, Age, Main Symptom, Duration, Additional Symptoms, Medical History.
- Provide educational information only.
- Recommend consulting a healthcare professional.
- If symptoms sound severe, advise urgent medical attention.
- After providing an assessment, continue to answer follow-up questions helpfully.

After collecting information, provide:
1. Summary of symptoms
2. Possible health concerns (not diagnoses)
3. General self-care suggestions
4. Warning signs to watch for
5. Recommendation to consult a healthcare professional

End assessments with:
"This information is educational and not a substitute for professional medical advice."
"""

# =========================
# SESSION STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "step" not in st.session_state:
    st.session_state.step = "name"

if "user_info" not in st.session_state:
    st.session_state.user_info = {}

# =========================
# FUNCTIONS
# =========================
def ask_groq(conversation_history):
    """Send full conversation history to Groq for context-aware responses."""
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add all conversation history
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.5,
            max_tokens=800
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error: {str(e)}"

# =========================
# TITLE
# =========================
st.title("🩺 MediBot")
st.warning(
    "Educational information only. Not a substitute for professional medical advice."
)

# =========================
# NEW CONSULTATION BUTTON
# =========================
if st.button("🔄 New Consultation"):
    st.session_state.messages = []
    st.session_state.user_info = {}
    st.session_state.step = "name"
    st.rerun()

# =========================
# INITIAL MESSAGE
# =========================
if len(st.session_state.messages) == 0:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello 👋 Welcome to MediBot.\n\nMay I know your name?"
    })

# =========================
# DISPLAY CHAT
# =========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# =========================
# CHAT INPUT
# =========================
user_input = st.chat_input("Type here...")

if user_input:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    reply = ""
    
    # =========================
    # NAME
    # =========================
    if st.session_state.step == "name":
        st.session_state.user_info["name"] = user_input
        reply = f"Nice to meet you, {user_input}! 😊\n\nHow old are you?"
        st.session_state.step = "age"
    
    # =========================
    # AGE
    # =========================
    elif st.session_state.step == "age":
        st.session_state.user_info["age"] = user_input
        reply = "Please describe your main symptom."
        st.session_state.step = "symptom"
    
    # =========================
    # MAIN SYMPTOM
    # =========================
    elif st.session_state.step == "symptom":
        st.session_state.user_info["symptom"] = user_input
        reply = "How long have you had this symptom?"
        st.session_state.step = "duration"
    
    # =========================
    # DURATION
    # =========================
    elif st.session_state.step == "duration":
        st.session_state.user_info["duration"] = user_input
        reply = "Do you have any additional symptoms?"
        st.session_state.step = "additional"
    
    # =========================
    # ADDITIONAL SYMPTOMS
    # =========================
    elif st.session_state.step == "additional":
        st.session_state.user_info["additional"] = user_input
        reply = "Do you have any medical history, allergies, or ongoing conditions?"
        st.session_state.step = "history"
    
    # =========================
    # HISTORY → GENERATE ASSESSMENT
    # =========================
    elif st.session_state.step == "history":
        st.session_state.user_info["history"] = user_input
        
        # Build context prompt with collected info
        context_prompt = f"""
Patient Information:
- Name: {st.session_state.user_info['name']}
- Age: {st.session_state.user_info['age']}
- Main Symptom: {st.session_state.user_info['symptom']}
- Duration: {st.session_state.user_info['duration']}
- Additional Symptoms: {st.session_state.user_info['additional']}
- Medical History: {st.session_state.user_info['history']}

Please provide an educational health summary based on this information.
"""
        # Temporarily add context as user message for the API call
        temp_messages = st.session_state.messages.copy()
        temp_messages[-1] = {"role": "user", "content": context_prompt}
        
        with st.spinner("Analyzing symptoms..."):
            reply = ask_groq(temp_messages)
        
        st.session_state.step = "followup"
    
    # =========================
    # FOLLOW-UP QUESTIONS (CONTINUOUS CONVERSATION)
    # =========================
    elif st.session_state.step == "followup":
        # Send full conversation history for context-aware follow-up
        with st.spinner("Thinking..."):
            reply = ask_groq(st.session_state.messages)

    else:
        reply = "Please start a new consultation."
    
    # Add assistant reply
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })
    
    st.rerun()
