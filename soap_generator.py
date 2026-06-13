import streamlit as st
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

conversation = """
Doctor: Good morning! What brings you in today?
Patient: I've had a terrible headache for the past 3 days. It's mostly on the left side.
Doctor: On a scale of 1 to 10 how bad is the pain?
Patient: Around a 7. I also feel nauseous and light hurts my eyes.
Doctor: Any fever or vomiting?
Patient: No fever but I did vomit once yesterday.
Doctor: Have you had migraines before?
Patient: Yes, a few times in the past but never this bad.
Doctor: I'm going to prescribe sumatriptan and recommend rest in a dark room.
"""

prompt = f"""
You are a clinical documentation assistant.
Given the following doctor-patient conversation, generate a structured SOAP note.

Conversation:
{conversation}

Format the output exactly like this:
SUBJECTIVE:
OBJECTIVE:
ASSESSMENT:
PLAN:
"""

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": prompt}
    ]
)

print(response.choices[0].message.content)