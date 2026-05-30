import os
import streamlit as st
from google import genai
from dotenv import load_dotenv
from utils.loader import load_and_chunk_pdf
from utils.retriever import VectorRetriever

# ── 1. Environment ────────────────────────────────────────────────────────────
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Missing API Key: Add GEMINI_API_KEY to your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)

# ── 2. Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Chelsea FC Intelligence",
    page_icon="⚽",
    layout="wide",
)

# ── 3. Chelsea FC Styling ─────────────────────────────────────────────────────
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@300;400;500;600&family=Barlow+Condensed:wght@400;700&display=swap');

    /* ── Global Canvas ── */
    .stApp {
        background-color: #0A0E1A !important;
        color: #E8E4D8 !important;
        font-family: 'Barlow', sans-serif !important;
    }

    /* Diagonal navy-to-midnight gradient background strip */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background:
            repeating-linear-gradient(
                -55deg,
                transparent,
                transparent 60px,
                rgba(26, 54, 107, 0.04) 60px,
                rgba(26, 54, 107, 0.04) 61px
            );
        pointer-events: none;
        z-index: 0;
    }

    /* ── Typography overrides ── */
    p, span, label, li, ul, ol, strong, em, div {
        color: #E8E4D8 !important;
        font-family: 'Barlow', sans-serif !important;
    }

    h1, h2, h3, h4 {
        font-family: 'Bebas Neue', sans-serif !important;
        color: #EAD37A !important;
        letter-spacing: 2px !important;
    }

    /* ── Markdown container ── */
    div[data-testid="stMarkdownContainer"] * {
        color: #E8E4D8 !important;
    }

    /* ── Chat messages ── */
    div[data-testid="stChatMessage"] {
        background-color: #111827 !important;
        border: 1px solid #1E3A6E !important;
        border-radius: 6px !important;
        margin-bottom: 0.75rem !important;
    }
    div[data-testid="stChatMessage"] * {
        color: #E8E4D8 !important;
    }

    /* User bubble slightly different shade */
    div[data-testid="stChatMessage"][data-testid*="user"] {
        border-left: 3px solid #EAD37A !important;
    }

    /* ── Expander (context chunks) ── */
    .stExpander {
        background-color: #0D1424 !important;
        border: 1px solid #1E3A6E !important;
        border-left: 3px solid #EAD37A !important;
        border-radius: 4px !important;
        margin-bottom: 1rem !important;
    }
    .stExpander summary, .stExpander * {
        color: #E8E4D8 !important;
    }

    /* ── Chat input ── */
    div[data-testid="stChatInput"] {
        background-color: #111827 !important;
        border: 1px solid #1E3A6E !important;
        border-radius: 6px !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: #111827 !important;
        color: #E8E4D8 !important;
        font-family: 'Barlow', sans-serif !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #5A6A8A !important;
    }

    /* ── Buttons ── */
    div[data-testid="stButton"] button {
        background-color: #1E3A6E !important;
        border: 1px solid #EAD37A !important;
        border-radius: 3px !important;
        color: #EAD37A !important;
        font-family: 'Barlow Condensed', sans-serif !important;
        font-size: 0.85rem !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        transition: background 0.2s !important;
    }
    div[data-testid="stButton"] button:hover {
        background-color: #EAD37A !important;
        color: #0A0E1A !important;
    }
    div[data-testid="stButton"] button * {
        color: inherit !important;
    }

    /* ── Toggle ── */
    div[data-testid="stToggle"] label {
        color: #A0AABF !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.5px !important;
    }

    /* ── Alerts ── */
    div[data-testid="stNotification"], .stAlert, div[role="alert"] {
        background-color: #0D1424 !important;
        border: 1px solid #EAD37A !important;
        border-radius: 4px !important;
    }
    div[data-testid="stNotification"] p, .stAlert p, div[role="alert"] p {
        color: #E8E4D8 !important;
    }

    /* ── Spinner ── */
    div[data-testid="stSpinner"] * {
        color: #EAD37A !important;
    }

    /* ── Divider ── */
    hr {
        border-color: #1E3A6E !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #0A0E1A; }
    ::-webkit-scrollbar-thumb { background: #1E3A6E; border-radius: 3px; }

    /* ── Badge chips ── */
    .cfc-badge {
        display: inline-block;
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 0.7rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #EAD37A;
        border: 1px solid #EAD37A;
        padding: 2px 8px;
        border-radius: 2px;
        margin-right: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# ── 4. Session State ───────────────────────────────────────────────────────────
if "retriever" not in st.session_state:
    st.session_state.retriever = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── 5. Auto-load the PDF ───────────────────────────────────────────────────────
target_pdf = os.path.join("data", "chelsea_fc.pdf")

if st.session_state.retriever is None:
    if os.path.exists(target_pdf):
        with st.spinner("Loading Chelsea FC knowledge base..."):
            try:
                chunks = load_and_chunk_pdf(target_pdf)
                retriever = VectorRetriever()
                retriever.add_documents(chunks)
                st.session_state.retriever = retriever
            except Exception as e:
                st.error(f"Initialisation failed: {e}")
                st.stop()
    else:
        st.error("⚠️ Document not found. Place `chelsea_fc.pdf` inside the `data/` directory.")
        st.stop()

# ── 6. Header ─────────────────────────────────────────────────────────────────
st.markdown("""
    <div style='padding: 1.5rem 0 1rem 0;'>
        <span class='cfc-badge'>Est. 1905</span>
        <span class='cfc-badge'>Stamford Bridge</span>
        <span class='cfc-badge'>The Blues</span>
        <h1 style='font-family:"Bebas Neue",sans-serif; font-size:3.5rem; color:#EAD37A; letter-spacing:4px; margin:0.75rem 0 0.25rem 0;'>
            Chelsea FC <span style='color:#E8E4D8; font-size:2rem;'>Intelligence Hub</span>
        </h1>
        <p style='font-size:0.95rem; color:#6A7A9F; margin:0;'>
            Ask anything about Chelsea's history, players, trophies, or managers.
        </p>
    </div>
""", unsafe_allow_html=True)
greeting_placeholder = st.empty()
# ── 7. Controls ────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    detailed_mode = st.toggle("Extended answers (more detail)", value=False)
with col2:
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown("<hr style='margin: 0.5rem 0 1.5rem 0;'>", unsafe_allow_html=True)

# ── 8. Message History ─────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# ── 9. Query Handler ───────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask about Chelsea FC..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Vector search
    context_chunks = st.session_state.retriever.retrieve_relevant_chunks(prompt, top_k=3)

    # Show retrieved chunks in expander
    if context_chunks:
        with st.expander("Reference Context Chunks"):
            for i, chunk in enumerate(context_chunks):
                st.markdown(f"**Chunk {i + 1}:**\n\n{chunk}")
                st.markdown("---")

    # Build prompt
    context_string = "\n\n".join(context_chunks)
    length_instruction = (
        " Provide a thorough, detailed response with supporting facts."
        if detailed_mode
        else " Be concise and direct."
    )

    system_instruction = (
    "You are an expert Chelsea FC analyst and historian with deep knowledge of the club. "
    "Use the provided context chunks as your primary source. "
    "If the context is incomplete, supplement with your own Chelsea FC knowledge to give a full, helpful answer. "
    "Never say you cannot answer a question about Chelsea FC."
    + length_instruction
    )

    full_payload = (
        f"{system_instruction}\n\n"
        f"--- CONTEXT START ---\n{context_string}\n--- CONTEXT END ---\n\n"
        f"Question: {prompt}"
    )

    # Stream the response
    with st.chat_message("assistant"):
        try:
            response_stream = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=full_payload,
            )
            full_response = st.write_stream(chunk.text for chunk in response_stream)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Model error: {e}")
            st.session_state.messages.pop()
