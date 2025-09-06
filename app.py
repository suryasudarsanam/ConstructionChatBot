import streamlit as st
import google.generativeai as genai
from db import init_db, save_message, load_messages, clear_messages
from dotenv import load_dotenv
import os

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="🏗️ Constructo Chatbot", layout="wide")

# Load .env and get API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ Gemini API key not found! Please set GEMINI_API_KEY in .env file.")
    st.stop()

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Init DB
init_db()

# ----------------------------
# Construction Keywords
# ----------------------------
CONSTRUCTION_KEYWORDS = [
    "concrete", "reinforcement","sand", "rebar", "masonry", "steel", "beam", "column",
    "foundation", "slab", "formwork", "excavation", "survey", "architect",
    "structural", "estimation", "cost estimate", "quantity", "BOQ", "schedule",
    "HVAC", "plumbing", "electrical", "MEP", "insulation", "roof", "tiling",
    "finishing", "site", "scaffolding", "crane", "safety", "PPE", "building",
    "construction", "contractor", "soil", "geotech", "drainage", "waterproofing",
    "sand mix","cement mix","sand cement mix ratio","cement"
]

def looks_construction_related(text: str) -> bool:
    text = text.lower()
    return any(kw in text for kw in CONSTRUCTION_KEYWORDS)

# ----------------------------
# APP STATE
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = load_messages()

# ----------------------------
# PROFESSIONAL STYLING
# ----------------------------
st.markdown(
    """
    <style>
    /* Global background */
    .main {
        background-color: #fafafa;
    }

    /* Title */
    .app-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1f2937; /* gray-800 */
        text-align: center;
        margin-bottom: 0.3rem;
    }

    .app-subtitle {
        text-align: center;
        font-size: 1rem;
        color: #6b7280; /* gray-500 */
        margin-bottom: 2rem;
    }

    /* Chat container */
    .stChatMessage {
        padding: 0.6rem 1rem;
        border-radius: 0.75rem;
        margin: 0.3rem 0;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    /* User bubble */
    [data-testid="stChatMessage-user"] {
        background-color: #2563eb; /* blue-600 */
        color: #ffffff;
        border-bottom-right-radius: 0.3rem !important;
        margin-left: auto;
        width: fit-content;
        max-width: 75%;
    }

    /* Assistant bubble */
    [data-testid="stChatMessage-assistant"] {
        background-color: #f3f4f6; /* gray-100 */
        color: #111827; /* gray-900 */
        border-bottom-left-radius: 0.3rem !important;
        margin-right: auto;
        width: fit-content;
        max-width: 75%;
    }

    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #1f2937 !important; /* dark gray */
        color: #f9fafb !important; /* light text */
        box-shadow: 2px 0 5px rgba(0,0,0,0.1);
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p {
        color: #f9fafb !important; /* white text */
    }

    /* Input box */
    .stChatInput textarea {
        border: 1px solid #d1d5db !important; /* gray-300 */
        border-radius: 0.5rem !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# SIDEBAR
# ----------------------------
st.sidebar.title("⚙️ Options")
if st.sidebar.button("🗑️ Clear Conversation"):
    clear_messages()
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("📂 Database: `chat_history.db`")

# ----------------------------
# HEADER
# ----------------------------
st.markdown("<div class='app-title'>🏗️ Constructo Chatbot</div>", unsafe_allow_html=True)
st.markdown("<div class='app-subtitle'>Your trusted assistant for construction-related queries only</div>", unsafe_allow_html=True)

# ----------------------------
# CHAT DISPLAY
# ----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------------------
# CHAT INPUT
# ----------------------------
if prompt := st.chat_input("Ask a construction-related question..."):
    # Save user message
    user_msg = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_msg)
    save_message("user", prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    # Check if related to construction
    if not looks_construction_related(prompt):
        reply = "🚧 I can answer construction-related queries only."
    else:
        try:
            response = model.generate_content(prompt)
            reply = response.text.strip()
        except Exception as e:
            reply = f"⚠️ Error calling Gemini API: {e}"

    # Save assistant reply
    bot_msg = {"role": "assistant", "content": reply}
    st.session_state.messages.append(bot_msg)
    save_message("assistant", reply)

    with st.chat_message("assistant"):
        st.markdown(reply)
