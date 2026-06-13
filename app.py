import json
import streamlit as st
from groq import Groq
import tempfile, os
from datetime import datetime

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="ClinDoc AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: #fdfaf5; color: #2d2a22; }

[data-testid="stSidebar"] { background: #fffef9 !important; border-right: 1px solid #e8e0cc; }
[data-testid="stSidebar"] * { color: #4a4030 !important; }

.sidebar-brand { font-family: 'Playfair Display', serif; font-size: 1.4rem; font-weight: 600; color: #b8860b !important; letter-spacing: -0.5px; margin-bottom: 0.2rem; }
.sidebar-tag { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 2px; color: #c9a84c !important; margin-bottom: 1.5rem; }
.sidebar-divider { border: none; border-top: 1px solid #e8e0cc; margin: 1.2rem 0; }
.sidebar-label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1.5px; color: #9a8a6a !important; margin-bottom: 0.3rem; }
.sidebar-value { font-size: 0.88rem; color: #4a4030 !important; margin-bottom: 1rem; }

.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #4caf7d; margin-right: 6px; animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

.main-header { background: linear-gradient(135deg, #fffbef 0%, #fff9e7 60%, #fef8c8 100%); border: 1px solid #e9d77a; border-radius: 16px; padding: 2.5rem 2.8rem; margin-bottom: 2rem; position: relative; overflow: hidden; }
.main-header::before { content: ''; position: absolute; top: -40px; right: -40px; width: 200px; height: 200px; background: radial-gradient(circle, rgba(220,175,58,0.18) 0%, transparent 70%); border-radius: 50%; }
.main-title { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 600; color: #2d2a29; margin: 0 0 0.4rem 0; line-height: 1.2; }
.main-subtitle { font-size: 0.92rem; color: #7a9a6a; margin: 0; font-weight: 400; }
.badge { display: inline-block; background: rgba(190,174,71,0.1); border: 1px solid rgba(184,134,11,0.35); color: #9a6f0a; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; padding: 3px 10px; border-radius: 20px; margin-bottom: 1rem; }

.card { background: #ffffff; border: 1px solid #ede6d0; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.2rem; box-shadow: 0 1px 4px rgba(180,150,80,0.07); }
.card-title { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; color: #b8860b; margin-bottom: 0.8rem; font-weight: 600; }

.soap-container { background: #ffffff; border-radius: 12px; padding: 2rem 2.2rem; color: #2d2a29; border: 1px solid #ede5d0; box-shadow: 0 2px 8px rgba(180,150,80,0.08); }
.soap-section { margin-bottom: 1.4rem; padding-bottom: 1.4rem; border-bottom: 1px solid #f0e8d8; }
.soap-section:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.soap-label { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 0.5rem; }
.soap-s { color: #1d7fa4; } .soap-o { color: #2e8d52; } .soap-a { color: #b8960b; } .soap-p { color: #7c8dbd; }
.soap-text { font-size: 0.9rem; color: #3d3520; line-height: 1.7; }
.soap-header-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid #f0e8d8; }
.soap-doc-title { font-family: 'Playfair Display', serif; font-size: 1.1rem; color: #2d2a29; font-weight: 600; }
.soap-meta { font-size: 0.75rem; color: #a89988; }

.med-card { background: #fffdf7; border: 1px solid #ede5d0; border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.75rem; box-shadow: 0 1px 3px rgba(180,150,80,0.06); }
.med-name { font-size: 0.95rem; font-weight: 600; color: #8a6800; margin-bottom: 0.3rem; }
.med-detail { font-size: 0.82rem; color: #6a8c3a; line-height: 1.6; }
.interaction-badge { display: inline-block; font-size: 0.68rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 2px 8px; border-radius: 4px; margin-bottom: 0.4rem; }
.badge-high { background: rgba(220,38,38,0.08); color: #b91c1c; border: 1px solid rgba(220,38,38,0.25); }
.badge-moderate { background: rgba(217,119,6,0.1); color: #b48909; border: 1px solid rgba(217,119,6,0.3); }
.badge-low { background: rgba(22,163,74,0.08); color: #15803d; border: 1px solid rgba(22,163,74,0.25); }
.suggest-card { background: #fffef9; border: 1px solid #e8d88a; border-left: 3px solid #c9a84c; border-radius: 0 10px 10px 0; padding: 0.9rem 1.1rem; margin-bottom: 0.65rem; }
.suggest-name { font-size: 0.9rem; font-weight: 600; color: #8a6800; margin-bottom: 0.2rem; }
.suggest-reason { font-size: 0.8rem; color: #7a6700; line-height: 1.5; }
.disclaimer { font-size: 0.72rem; color: #9a8a9a; background: #fffbef; border: 1px solid #e8d88a; border-radius: 8px; padding: 0.6rem 0.9rem; margin-top: 1rem; line-height: 1.5; }

[data-testid="stTextInput"] input { background: #ffffff !important; border: 1px solid #ddd0b8 !important; border-radius: 8px !important; color: #2d2a22 !important; font-family: 'Inter', sans-serif !important; }
[data-testid="stTextInput"] input:focus { border-color: #c9a84c !important; box-shadow: 0 0 0 2px rgba(220,188,86,0.15) !important; }
[data-testid="stTextArea"] textarea { background: #ffffff !important; border: 1px solid #ddd0b8 !important; border-radius: 8px !important; color: #2d2a22 !important; font-family: 'Inter', sans-serif !important; font-size: 0.88rem !important; line-height: 1.6 !important; }
[data-testid="stFileUploader"] { background: #fffdf7 !important; border: 1px dashed #d4bc80 !important; border-radius: 8px !important; }

.stButton > button { background: linear-gradient(135deg, #d4a017 0%, #b8770b 100%) !important; color: #ffffff !important; border: none !important; border-radius: 8px !important; padding: 0.6rem 2rem !important; font-family: 'Inter', sans-serif !important; font-weight: 600 !important; font-size: 0.9rem !important; letter-spacing: 0.3px !important; width: 100% !important; transition: opacity 0.2s !important; box-shadow: 0 2px 8px rgba(184,134,11,0.25) !important; }
.stButton > button:hover { opacity: 0.88 !important; }
[data-testid="stDownloadButton"] button { background: #fffdf7 !important; color: #8a7900 !important; border: 1px solid #d4bc80 !important; border-radius: 8px !important; font-family: 'Inter', sans-serif !important; font-size: 0.85rem !important; width: 100% !important; }

[data-testid="stSpinner"] { color: #b8860b !important; }
.stAlert { border-radius: 8px !important; border: none !important; }
.section-label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1.5px; color: #9a8a6a; font-weight: 600; margin-bottom: 0.5rem; margin-top: 1.2rem; }

[data-testid="stTabs"] [data-baseweb="tab"] { color: #7a6940 !important; }
[data-testid="stTabs"] [aria-selected="true"] { color: #b8960b !important; border-bottom-color: #b9660b !important; }

/* ── Score meter ── */
.score-ring-wrap { display: flex; align-items: center; gap: 1.4rem; background: #fffdf7; border: 1px solid #ede5d0; border-radius: 12px; padding: 1.1rem 1.4rem; margin-bottom: 1rem; }
.score-circle { width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: 700; flex-shrink: 0; }
.score-excellent { background: rgba(22,163,74,0.12); color: #15803d; border: 3px solid #16a34a; }
.score-good      { background: rgba(59,130,246,0.10); color: #1d4ed8; border: 3px solid #3b82f6; }
.score-fair      { background: rgba(217,119,6,0.10);  color: #b45309; border: 3px solid #d97706; }
.score-poor      { background: rgba(220,38,38,0.08);  color: #b91c1c; border: 3px solid #dc2626; }
.score-label { font-size: 1rem; font-weight: 600; color: #2d2a22; }
.score-sub   { font-size: 0.78rem; color: #7a6940; margin-top: 0.2rem; }
.score-bar-wrap { margin-top: 0.5rem; background: #f0e8d8; border-radius: 999px; height: 6px; width: 100%; }
.score-bar { height: 6px; border-radius: 999px; transition: width 0.6s ease; }

/* ── Approve banner ── */
.approve-banner { background: linear-gradient(135deg,#f0fdf4,#dcfce7); border: 1px solid #86efac; border-radius: 10px; padding: 0.9rem 1.2rem; margin-top: 1rem; display:flex; align-items:center; gap:0.8rem; }
.approve-icon { font-size: 1.3rem; }
.approve-text { font-size: 0.85rem; color: #166534; font-weight: 500; }

/* ── Before/After split ── */
.split-label { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 0.5rem; padding: 0.3rem 0.7rem; border-radius: 6px; display:inline-block; }
.split-left-label  { background: rgba(59,130,246,0.08); color: #1d4ed8; }
.split-right-label { background: rgba(22,163,74,0.08);  color: #15803d; }
.transcript-box { background: #f8f6f0; border: 1px solid #e0d8c0; border-radius: 10px; padding: 1.1rem 1.3rem; font-size: 0.85rem; color: #4a4030; line-height: 1.8; min-height: 300px; white-space: pre-wrap; }

/* ── Language chip ── */
.lang-chip { display:inline-block; background: rgba(184,134,11,0.10); border:1px solid rgba(184,134,11,0.3); color:#7a5900; font-size:0.72rem; font-weight:600; letter-spacing:1px; padding:3px 10px; border-radius:20px; margin-bottom:0.5rem; }

/* ── Record button ── */
.rec-hint { font-size:0.75rem; color:#7a6940; margin-top:0.4rem; line-height:1.5; }
</style>
""", unsafe_allow_html=True)

# ── Groq client ──────────────────────────────────────────────
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ── Session history helpers ───────────────────────────────────
HISTORY_FILE = 'session_history.json'

def load_history():
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_session(patient_name, transcript, soap_text, language="English"):
    history = load_history()
    session = {
        'id': str(datetime.now().timestamp()),
        'patient': patient_name or 'Unnamed patient',
        'date': datetime.now().strftime('%d %b %Y, %I:%M %p'),
        'transcript': transcript,
        'soap': soap_text,
        'language': language
    }
    history.insert(0, session)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

def delete_session(session_id):
    history = load_history()
    history = [s for s in history if s['id'] != session_id]
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

# ── Medication analysis helper ────────────────────────────────
def analyse_medications(soap_text):
    med_prompt = f"""You are a clinical pharmacology assistant. Analyse this SOAP note and return ONLY a JSON object — no explanation, no markdown, no code fences.

SOAP Note:
{soap_text}

Return exactly this structure:
{{
  "extracted": [
    {{"name": "medication name", "dose": "dose if mentioned or unknown", "purpose": "why it is being used"}}
  ],
  "interactions": [
    {{"drugs": "Drug A + Drug B", "severity": "High or Moderate or Low", "description": "what the interaction is"}}
  ],
  "suggestions": [
    {{"name": "medication name", "reason": "why it may be appropriate based on the diagnosis"}}
  ]
}}

If no medications are found, return empty arrays. Keep suggestions to 3 or fewer. Only include clinically relevant interactions."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": med_prompt}]
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

# ── Completeness Score helper ─────────────────────────────────
def compute_completeness_score(sections):
    score = 0
    feedback = []

    for key, text in sections.items():
        stripped = text.strip()
        if not stripped:
            feedback.append(f"⚠️ {key.capitalize()} section is empty")
            continue
        words = len(stripped.split())
        if words >= 20:
            score += 25
        elif words >= 8:
            score += 15
            feedback.append(f"💡 {key.capitalize()} section could be more detailed")
        else:
            score += 5
            feedback.append(f"⚠️ {key.capitalize()} section is very brief")

    # Bonus: check for key clinical terms
    full_text = " ".join(sections.values()).lower()
    if any(w in full_text for w in ["diagnosis", "assessment", "impression"]):
        score = min(score + 5, 100)
    if any(w in full_text for w in ["follow", "refer", "prescri", "monitor"]):
        score = min(score + 5, 100)

    return min(score, 100), feedback

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">ClinDoc AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tag">Clinical Assistant</div>', unsafe_allow_html=True)
    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">Status</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-value"><span class="status-dot"></span>Online — Groq + LLaMA 3.3</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">Built by</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-value">Krithika Vijay</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">Model</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-value">LLaMA 3.3 70B + Whisper V3</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">Purpose</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-value">Ambient clinical documentation — voice or text to structured SOAP notes</div>', unsafe_allow_html=True)

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-label">Note</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-value" style="font-size:0.75rem; color:#4a6080 !important;">For demonstration purposes only. Not for real clinical use.</div>', unsafe_allow_html=True)

    # ── Session History ───────────────────────────────────────
    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-label">🕓 Session History</div>', unsafe_allow_html=True)

    history = load_history()
    if not history:
        st.markdown('<div class="sidebar-value" style="font-size:0.75rem; color:#4a6080 !important;">No sessions yet. Generate a SOAP note to save one.</div>', unsafe_allow_html=True)
    else:
        for session in history:
            lang_tag = session.get('language', 'English')
            with st.expander(f"**{session['patient']}** · {session['date']}"):
                st.markdown(f'<span class="lang-chip">🌐 {lang_tag}</span>', unsafe_allow_html=True)
                st.markdown(session['soap'], unsafe_allow_html=True)
                if st.button('🗑 Delete this session', key=f"del_{session['id']}"):
                    delete_session(session['id'])
                    st.rerun()

# ── Main content ──────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <div class="badge">GenAI · Healthcare</div>
    <div class="main-title">Ambient Clinical Documentation</div>
    <p class="main-subtitle">Convert doctor–patient conversations into structured SOAP notes — instantly.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.1, 0.9], gap="large")

with col1:
    st.markdown('<div class="card-title">Patient & Input</div>', unsafe_allow_html=True)
    patient_name = st.text_input("Patient name", placeholder="e.g. Aisha Sharma (optional)")

    # ── NEW: Language selector ────────────────────────────────
    st.markdown('<div class="section-label">Language / भाषा / மொழி</div>', unsafe_allow_html=True)
    LANGUAGE_OPTIONS = {
        "English": "en",
        "Hindi (हिंदी)": "hi",
        "Tamil (தமிழ்)": "ta",
        "Kannada (ಕನ್ನಡ)": "kn",
        "Telugu (తెలుగు)": "te",
        "Bengali (বাংলা)": "bn",
        "Marathi (मराठी)": "mr",
    }
    selected_language = st.selectbox(
        "Language",
        options=list(LANGUAGE_OPTIONS.keys()),
        label_visibility="collapsed"
    )
    lang_code = LANGUAGE_OPTIONS[selected_language]

    # ── Patient History ────────────────────────────────────────
    st.markdown('<div class="section-label">Patient history (optional)</div>', unsafe_allow_html=True)
    patient_history = st.text_area(
        "Patient history",
        placeholder="Paste prior visit notes, known conditions, allergies, current medications…",
        height=100,
        label_visibility="collapsed"
    )

    # ── NEW: Real-time audio recording via HTML component ─────
    st.markdown('<div class="section-label">🎙️ Record audio (live)</div>', unsafe_allow_html=True)

    # Inject a mic recorder using browser's MediaRecorder API
    recorder_html = """
<div style="background:#fffdf7; border:1px dashed #d4bc80; border-radius:8px; padding:1rem 1.2rem; margin-bottom:0.5rem;">
  <div style="display:flex; gap:0.7rem; align-items:center; flex-wrap:wrap;">
    <button id="startBtn" onclick="startRec()"
      style="background:linear-gradient(135deg,#d4a017,#b8770b);color:#fff;border:none;border-radius:6px;
             padding:0.45rem 1.1rem;font-size:0.82rem;font-weight:600;cursor:pointer;">
      ● Start Recording
    </button>
    <button id="stopBtn" onclick="stopRec()" disabled
      style="background:#f0e8d8;color:#7a6940;border:1px solid #d4bc80;border-radius:6px;
             padding:0.45rem 1.1rem;font-size:0.82rem;font-weight:600;cursor:pointer;">
      ■ Stop
    </button>
    <span id="recStatus" style="font-size:0.78rem;color:#7a6940;"></span>
  </div>
  <audio id="audioPlayback" controls style="width:100%;margin-top:0.8rem;display:none;border-radius:6px;"></audio>
  <div id="downloadWrap" style="margin-top:0.6rem;display:none;">
    <a id="downloadLink" style="font-size:0.78rem;color:#b8860b;font-weight:600;text-decoration:none;">
      ⬇ Download recorded audio
    </a>
    <p style="font-size:0.72rem;color:#9a8a6a;margin-top:0.3rem;line-height:1.5;">
      Save this file, then upload it below to transcribe.
    </p>
  </div>
</div>
<script>
let mediaRecorder, chunks = [];
async function startRec() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({audio:true});
    mediaRecorder = new MediaRecorder(stream);
    chunks = [];
    mediaRecorder.ondataavailable = e => chunks.push(e.data);
    mediaRecorder.onstop = () => {
      const blob = new Blob(chunks, {type:'audio/webm'});
      const url  = URL.createObjectURL(blob);
      const audio = document.getElementById('audioPlayback');
      audio.src = url;
      audio.style.display = 'block';
      const dl = document.getElementById('downloadLink');
      dl.href = url;
      dl.download = 'recording_' + Date.now() + '.webm';
      document.getElementById('downloadWrap').style.display = 'block';
      document.getElementById('recStatus').textContent = '✓ Recording saved';
    };
    mediaRecorder.start();
    document.getElementById('startBtn').disabled = true;
    document.getElementById('stopBtn').disabled  = false;
    document.getElementById('recStatus').innerHTML = '<span style="color:#e53e3e;">⏺ Recording…</span>';
  } catch(err) {
    document.getElementById('recStatus').textContent = '⚠ Mic access denied: ' + err.message;
  }
}
function stopRec() {
  mediaRecorder.stop();
  document.getElementById('startBtn').disabled = false;
  document.getElementById('stopBtn').disabled  = true;
}
</script>
"""
    st.components.v1.html(recorder_html, height=200)
    st.markdown('<div class="rec-hint">Record → Stop → Download → upload the file below to auto-transcribe.</div>', unsafe_allow_html=True)

    # ── Audio file upload ─────────────────────────────────────
    st.markdown('<div class="section-label">Upload audio recording</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["mp3", "wav", "m4a", "webm", "ogg"], label_visibility="collapsed")

    transcribed = ""
    if uploaded_file:
        with st.spinner("Transcribing audio…"):
            from transcribe import transcribe_audio
            suffix = "." + uploaded_file.name.split(".")[-1] if "." in uploaded_file.name else ".webm"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
                f.write(uploaded_file.read())
                tmp_path = f.name
            # Pass language code to Whisper for better accuracy
            transcribed = transcribe_audio(tmp_path, language=lang_code if lang_code != "en" else None)
            os.unlink(tmp_path)
        st.success("Audio transcribed successfully")

    st.markdown('<div class="section-label">Conversation transcript</div>', unsafe_allow_html=True)
    conversation = st.text_area(
        "Conversation",
        value=transcribed,
        height=180,
        label_visibility="collapsed",
        placeholder="Paste or type the doctor–patient conversation here…"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    generate = st.button("Generate SOAP Note →")

# ── Right column: output ──────────────────────────────────────
with col2:
    st.markdown('<div class="card-title">SOAP Note Output</div>', unsafe_allow_html=True)

    if generate:
        if not conversation.strip():
            st.warning("Please add a conversation first.")
        else:
            with st.spinner("Generating note…"):
                lang_instruction = (
                    f"Generate the SOAP note in {selected_language}. "
                    if selected_language != "English"
                    else ""
                )
                history_block = (
                    f"\nPatient History:\n{patient_history}\n"
                    if patient_history.strip()
                    else ""
                )
                prompt = f"""You are a clinical documentation assistant.
Given the following doctor-patient conversation, generate a structured SOAP note.
{lang_instruction}
{"Patient name: " + patient_name if patient_name else ""}
{history_block}
Conversation:
{conversation}

Format the output exactly like this:
SUBJECTIVE:
[text]

OBJECTIVE:
[text]

ASSESSMENT:
[text]

PLAN:
[text]"""

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                raw = response.choices[0].message.content

            # ── Parse SOAP sections ───────────────────────────
            sections = {"SUBJECTIVE": "", "OBJECTIVE": "", "ASSESSMENT": "", "PLAN": ""}
            current = None
            for line in raw.splitlines():
                stripped = line.strip()
                if stripped.upper().startswith("SUBJECTIVE"):
                    current = "SUBJECTIVE"
                elif stripped.upper().startswith("OBJECTIVE"):
                    current = "OBJECTIVE"
                elif stripped.upper().startswith("ASSESSMENT"):
                    current = "ASSESSMENT"
                elif stripped.upper().startswith("PLAN"):
                    current = "PLAN"
                elif current:
                    sections[current] += line + "\n"

            now = datetime.now().strftime("%d %B %Y · %I:%M %p")
            name_display = patient_name if patient_name else "—"
            colors = {"SUBJECTIVE": "soap-s", "OBJECTIVE": "soap-o", "ASSESSMENT": "soap-a", "PLAN": "soap-p"}

            # ── Completeness score ────────────────────────────
            score, score_feedback = compute_completeness_score(sections)
            if score >= 85:
                ring_class, score_word = "score-excellent", "Excellent"
                bar_color, bar_pct = "#16a34a", score
            elif score >= 65:
                ring_class, score_word = "score-good", "Good"
                bar_color, bar_pct = "#3b82f6", score
            elif score >= 40:
                ring_class, score_word = "score-fair", "Fair"
                bar_color, bar_pct = "#d97706", score
            else:
                ring_class, score_word = "score-poor", "Needs work"
                bar_color, bar_pct = "#dc2626", score

            # ── Build SOAP HTML ───────────────────────────────
            soap_html = f"""
<div class="soap-container">
  <div class="soap-header-bar">
    <div class="soap-doc-title">SOAP Note — {name_display}</div>
    <div class="soap-meta">{now} &nbsp;·&nbsp; 🌐 {selected_language}</div>
  </div>
"""
            for section, text in sections.items():
                c = colors[section]
                soap_html += f"""
  <div class="soap-section">
    <div class="soap-label {c}">{section}</div>
    <div class="soap-text">{text.strip().replace(chr(10), '<br>')}</div>
  </div>"""
            soap_html += "</div>"

            # ── Tabs ──────────────────────────────────────────
            tab1, tab2, tab3, tab4 = st.tabs([
                "📋 SOAP Note",
                "🔀 Before / After",
                "📊 Quality Score",
                "💊 Medications"
            ])

            # ═══════════ TAB 1 — SOAP Note ═══════════════════
            with tab1:
                # Edit & Approve workflow
                if "approved" not in st.session_state:
                    st.session_state.approved = False
                if "edited_soap" not in st.session_state:
                    st.session_state.edited_soap = raw

                if st.session_state.approved:
                    st.markdown("""
<div class="approve-banner">
  <div class="approve-icon">✅</div>
  <div class="approve-text">Note approved and locked. Download below.</div>
</div>""", unsafe_allow_html=True)
                    st.markdown(soap_html, unsafe_allow_html=True)
                else:
                    st.markdown(soap_html, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown('<div class="section-label">✏️ Edit note before approving</div>', unsafe_allow_html=True)
                    edited = st.text_area(
                        "Edit SOAP note",
                        value=st.session_state.edited_soap,
                        height=200,
                        label_visibility="collapsed",
                        key="soap_editor"
                    )
                    st.session_state.edited_soap = edited

                    approve_col, _ = st.columns([1, 1])
                    with approve_col:
                        if st.button("✅ Approve Note"):
                            st.session_state.approved = True
                            st.rerun()

                final_text = st.session_state.edited_soap
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button(
                    "⬇️ Download SOAP Note",
                    final_text,
                    file_name=f"SOAP_{patient_name or 'note'}_{datetime.now().strftime('%Y%m%d')}.txt"
                )

            # ═══════════ TAB 2 — Before / After ══════════════
            with tab2:
                st.markdown("**Raw transcript vs. structured SOAP note — side by side.**")
                st.markdown("<br>", unsafe_allow_html=True)
                left, right = st.columns(2, gap="medium")
                with left:
                    st.markdown('<span class="split-label split-left-label">📝 Raw Transcript</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="transcript-box">{conversation}</div>', unsafe_allow_html=True)
                with right:
                    st.markdown('<span class="split-label split-right-label">✅ Structured SOAP Note</span>', unsafe_allow_html=True)
                    st.markdown(soap_html, unsafe_allow_html=True)

            # ═══════════ TAB 3 — Quality Score ═══════════════
            with tab3:
                st.markdown(f"""
<div class="score-ring-wrap">
  <div class="score-circle {ring_class}">{score}</div>
  <div style="flex:1;">
    <div class="score-label">Completeness Score — {score_word}</div>
    <div class="score-sub">Based on section depth, clinical detail & key term coverage</div>
    <div class="score-bar-wrap">
      <div class="score-bar" style="width:{bar_pct}%; background:{bar_color};"></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

                st.markdown("**Section breakdown**")
                for section, text in sections.items():
                    words = len(text.strip().split()) if text.strip() else 0
                    bar_w = min(int(words / 40 * 100), 100)
                    c = colors[section]
                    st.markdown(f"""
<div style="margin-bottom:0.8rem;">
  <div style="display:flex; justify-content:space-between; margin-bottom:0.25rem;">
    <span class="soap-label {c}" style="font-size:0.68rem;">{section}</span>
    <span style="font-size:0.75rem; color:#7a6940;">{words} words</span>
  </div>
  <div style="background:#f0e8d8; border-radius:999px; height:5px;">
    <div style="width:{bar_w}%; background:{bar_color}; height:5px; border-radius:999px;"></div>
  </div>
</div>""", unsafe_allow_html=True)

                if score_feedback:
                    st.markdown("<br>**Suggestions to improve**")
                    for fb in score_feedback:
                        st.markdown(f"- {fb}")
                else:
                    st.success("All sections look comprehensive!")

            # ═══════════ TAB 4 — Medications ═════════════════
            with tab4:
                with st.spinner("Analysing medications…"):
                    try:
                        med_data = analyse_medications(raw)

                        st.markdown('<div class="card-title">Medications mentioned</div>', unsafe_allow_html=True)
                        if med_data.get("extracted"):
                            for med in med_data["extracted"]:
                                st.markdown(f"""
<div class="med-card">
  <div class="med-name">💊 {med.get('name', 'Unknown')}</div>
  <div class="med-detail"><strong>Dose:</strong> {med.get('dose', 'Not specified')}</div>
  <div class="med-detail"><strong>Purpose:</strong> {med.get('purpose', 'Not specified')}</div>
</div>""", unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="med-detail" style="color:#4a6080; padding:0.5rem 0;">No medications found in this note.</div>', unsafe_allow_html=True)

                        st.markdown('<br><div class="card-title">Interaction flags</div>', unsafe_allow_html=True)
                        if med_data.get("interactions"):
                            for ix in med_data["interactions"]:
                                sev = ix.get("severity", "Low")
                                badge_class = "badge-high" if sev == "High" else "badge-moderate" if sev == "Moderate" else "badge-low"
                                st.markdown(f"""
<div class="med-card">
  <span class="interaction-badge {badge_class}">{sev} risk</span>
  <div class="med-name" style="font-size:0.88rem;">{ix.get('drugs', '')}</div>
  <div class="med-detail">{ix.get('description', '')}</div>
</div>""", unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="med-detail" style="color:#34d399; padding:0.5rem 0;">✓ No known interactions flagged.</div>', unsafe_allow_html=True)

                        st.markdown('<br><div class="card-title">Suggested medications</div>', unsafe_allow_html=True)
                        if med_data.get("suggestions"):
                            for s in med_data["suggestions"]:
                                st.markdown(f"""
<div class="suggest-card">
  <div class="suggest-name">{s.get('name', '')}</div>
  <div class="suggest-reason">{s.get('reason', '')}</div>
</div>""", unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="med-detail" style="color:#4a6080; padding:0.5rem 0;">No additional suggestions.</div>', unsafe_allow_html=True)

                        st.markdown('<div class="disclaimer">⚠️ For demonstration only. Always verify medications with a licensed pharmacist or physician before clinical use.</div>', unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"Could not parse medication data: {e}")

            # Save to history
            save_session(patient_name, conversation, raw, language=selected_language)
            # Reset approval state for next run
            st.session_state.approved = False
            st.session_state.edited_soap = raw

    else:
        st.markdown("""
<div style="height:340px; background:#fffdf7; border:1px dashed #d4bc80;
     border-radius:12px; display:flex; align-items:center; justify-content:center;
     flex-direction:column; gap:0.5rem;">
  <div style="font-size:2rem;">📋</div>
  <div style="font-size:0.85rem; color:#4a6080;">Your SOAP note will appear here</div>
</div>
""", unsafe_allow_html=True)