import os
import json
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from personalities import PERSONALITIES, GROQ_MODELS, DEFAULT_MODEL, DEFAULT_PERSONALITY

load_dotenv()

st.set_page_config(
    page_title="AI Personality Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY", "")

    if not api_key or api_key == "your_key_here":
        st.error(
            "Groq API key not found.\n\n"
            "Local: Add it to your .env file:\n"
            "```\nGROQ_API_KEY=your_key_here\n```\n"
            "Streamlit Cloud: Go to App Settings -> Secrets and add:\n"
            "```\nGROQ_API_KEY = \"your_key_here\"\n```\n"
            "Get your key at https://console.groq.com"
        )
        st.stop()

    return Groq(api_key=api_key)


def inject_css(theme_mode: str):
    # Dynamic colors based on light/dark toggle
    if theme_mode == "Light":
        bg_main = "#F8FAFC"
        bg_sidebar = "#FFFFFF"
        border_color = "#CBD5E1"
        text_primary = "#000000"
        text_muted = "#475569"
        chat_bg = "#FFFFFF"
        chat_user_bg = "#F1F5F9"
        card_bg = "#FFFFFF"
    else:
        bg_main = "#0F0F1A"
        bg_sidebar = "#13131F"
        border_color = "#1E1E35"
        text_primary = "#E0E0FF"
        text_muted = "#6B7280"
        chat_bg = "#13131F"
        chat_user_bg = "#1A1A2E"
        card_bg = "#1A1A2E"

    st.markdown(f"""
    <style>
    /* ── Google Fonts (Poppins) ────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    /* ── Global resets ─────────────────────────────────────── */
    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
    }}
    .stApp {{
        background: {bg_main};
        color: {text_primary} !important;
    }}

    /* ── Input bar fixed at bottom ─────────────────────────── */
    [data-testid="stBottom"] {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: {bg_main};
        z-index: 100;
        padding: 1rem 0;
    }}

    /* ── Sidebar ────────────────────────────────────────────── */
    [data-testid="stSidebar"] {{
        background: {bg_sidebar} !important;
        border-right: 1px solid {border_color};
    }}
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {{
        color: {text_primary} !important;
    }}

    /* ── Sidebar logo / header ──────────────────────────────── */
    .sidebar-logo {{
        text-align: center;
        padding: 1.5rem 0 1rem;
    }}
    .sidebar-logo .bot-icon {{
        font-size: 3rem;
        line-height: 1;
    }}
    .sidebar-logo h1 {{
        color: #7C3AED;
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0.5rem 0 0.2rem;
        letter-spacing: -0.02em;
    }}
    .sidebar-logo p {{
        color: {text_muted};
        font-size: 0.75rem;
        margin: 0;
    }}

    /* ── Section labels ─────────────────────────────────────── */
    .section-label {{
        color: {text_muted};
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 1.5rem 0 0.5rem;
    }}

    /* ── Allowed topics list ────────────────────────────────── */
    .topic-pill {{
        display: inline-block;
        background: {card_bg};
        color: #7C3AED;
        border: 1px solid {border_color};
        border-radius: 20px;
        padding: 0.2rem 0.7rem;
        font-size: 0.72rem;
        margin: 0.2rem 0.2rem 0.2rem 0;
        font-weight: 500;
    }}

    /* ── Main content area ──────────────────────────────────── */
    .main-header {{
        text-align: center;
        padding: 1rem 0 0.5rem;
    }}
    .main-header h2 {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {text_primary} !important;
        margin: 0;
        letter-spacing: -0.03em;
    }}
    .main-header .subtitle {{
        color: {text_muted};
        font-size: 0.85rem;
        margin-top: 0.3rem;
    }}

    /* ── Gradient divider ───────────────────────────────────── */
    .gradient-divider {{
        height: 2px;
        border-radius: 2px;
        margin: 0.75rem 0 1.5rem;
    }}

    /* ── Chat messages ──────────────────────────────────────── */
    [data-testid="stChatMessage"] {{
        background: {chat_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 12px !important;
        margin-bottom: 0.75rem !important;
        color: {text_primary} !important;
    }}
    [data-testid="stChatMessage"] p {{
        color: {text_primary} !important;
    }}
    [data-testid="stChatMessage"][data-testid*="user"] {{
        background: {chat_user_bg} !important;
        border-color: {border_color} !important;
    }}

    /* ── Suggested prompts ──────────────────────────────────── */
    .suggested-label {{
        color: {text_muted};
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }}
    .stButton > button {{
        background: {card_bg} !important;
        color: {text_primary} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
        font-size: 0.78rem !important;
        padding: 0.45rem 0.85rem !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
        text-align: left !important;
        width: 100% !important;
        white-space: normal !important;
        height: auto !important;
        line-height: 1.4 !important;
    }}
    .stButton > button:hover {{
        border-color: #7C3AED !important;
    }}

    /* ── Chat input ─────────────────────────────────────────── */
    [data-testid="stChatInput"] {{
        background: {chat_bg} !important;
        border-color: {border_color} !important;
        border-radius: 12px !important;
    }}
    [data-testid="stChatInput"] textarea {{
        color: {text_primary} !important;
    }}
    [data-testid="stChatInput"]:focus-within {{
        border-color: #7C3AED !important;
    }}

    /* ── Select boxes ───────────────────────────────────────── */
    .stSelectbox [data-baseweb="select"] {{
        background: {card_bg} !important;
        border-color: {border_color} !important;
        border-radius: 8px !important;
        color: {text_primary} !important;
    }}
    .stSelectbox div {{
        color: {text_primary} !important;
    }}

    /* ── Clear button (danger) ──────────────────────────────── */
    .clear-btn > button {{
        background: transparent !important;
        color: #EF4444 !important;
        border-color: #EF4444 !important;
    }}
    .clear-btn > button:hover {{
        background: #1F0A0A !important;
        border-color: #DC2626 !important;
    }}

    /* ── Stats strip ─────────────────────────────────────────── */
    .stats-strip {{
        display: flex;
        gap: 1rem;
        margin: 0.5rem 0 1.25rem;
        flex-wrap: wrap;
    }}
    .stat-chip {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 6px;
        padding: 0.3rem 0.7rem;
        font-size: 0.72rem;
        color: {text_muted};
    }}
    .stat-chip span {{
        color: #7C3AED;
        font-weight: 600;
    }}

    /* ── Spinner color fix ──────────────────────────────────── */
    .stSpinner > div {{ border-top-color: #7C3AED !important; }}

    /* ── Scrollbar ──────────────────────────────────────────── */
    ::-webkit-scrollbar {{ width: 4px; }}
    ::-webkit-scrollbar-track {{ background: {bg_main}; }}
    ::-webkit-scrollbar-thumb {{ background: {border_color}; border-radius: 4px; }}

    /* ── Hide Streamlit default chrome ─────────────────────── */
    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{ padding-top: 1rem !important; padding-bottom: 6rem !important; }}
    </style>
    """, unsafe_allow_html=True)


def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = {}   # dict keyed by personality name
    if "personality" not in st.session_state:
        st.session_state.personality = DEFAULT_PERSONALITY
    if "model" not in st.session_state:
        st.session_state.model = DEFAULT_MODEL
    if "theme" not in st.session_state:
        st.session_state.theme = "Dark"
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None
    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = 0
    if "msg_count" not in st.session_state:
        st.session_state.msg_count = 0


def render_sidebar():
    with st.sidebar:
        # ── Logo / branding ─────────────────────────────────
        st.markdown("""
        <div class="sidebar-logo">
            <div class="bot-icon">🤖</div>
            <h1>AI Personality<br>Chatbot</h1>
            <p>Powered by Groq · 7 Expert Modes</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ── Theme Toggle ─────────────────────────────────────
        st.markdown('<div class="section-label">Appearance</div>', unsafe_allow_html=True)
        selected_theme = st.radio(
            "Theme Mode",
            options=["Dark", "Light"],
            index=0 if st.session_state.theme == "Dark" else 1,
            horizontal=True,
            label_visibility="collapsed"
        )
        if selected_theme != st.session_state.theme:
            st.session_state.theme = selected_theme
            st.rerun()

        st.divider()

        # ── Personality picker ───────────────────────────────
        st.markdown('<div class="section-label">Personality</div>', unsafe_allow_html=True)

        personality_names = list(PERSONALITIES.keys())

        current_idx = personality_names.index(st.session_state.personality)

        selected_personality = st.selectbox(
            label="Choose personality",
            options=personality_names,
            index=current_idx,
            label_visibility="collapsed",
        )

        if selected_personality != st.session_state.personality:
            st.session_state.personality = selected_personality
            st.rerun()

        # ── Personality info ─────────────────────────────────
        p = PERSONALITIES[st.session_state.personality]

        st.markdown('<div class="section-label">Allowed Topics</div>', unsafe_allow_html=True)
        topic_pills = "".join(
            f'<span class="topic-pill">{t}</span>' for t in p["allowed_topics"]
        )
        st.markdown(f'<div>{topic_pills}</div>', unsafe_allow_html=True)

        st.divider()

        # ── Model picker ─────────────────────────────────────
        st.markdown('<div class="section-label">AI Model</div>', unsafe_allow_html=True)

        selected_model = st.selectbox(
            label="Choose Groq model",
            options=GROQ_MODELS,
            index=GROQ_MODELS.index(st.session_state.model),
            label_visibility="collapsed",
        )

        if selected_model != st.session_state.model:
            st.session_state.model = selected_model

        st.divider()

        # ── Session stats ─────────────────────────────────────
        st.markdown('<div class="section-label">Session Stats</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="stats-strip">
                <div class="stat-chip">Messages <span>{st.session_state.msg_count}</span></div>
                <div class="stat-chip">Tokens <span>{st.session_state.total_tokens:,}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Clear chat ────────────────────────────────────────
        st.markdown('<div class="section-label">Actions</div>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
            if st.button("Clear Current Chat", use_container_width=True):
                st.session_state.messages[st.session_state.personality] = []
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Footer ────────────────────────────────────────────
        st.markdown("""
        <div style="text-align:center; color:#6B7280; font-size:0.68rem; margin-top:2rem; padding-top:1rem; border-top:1px solid #1E1E35;">
            Built with Streamlit + Groq<br>
            <a href="https://console.groq.com" target="_blank" style="color:#7C3AED;">Get API Key -></a>
        </div>
        """, unsafe_allow_html=True)


def render_header():
    p    = PERSONALITIES[st.session_state.personality]
    name = st.session_state.personality

    col_title, col_download = st.columns([8, 2])

    with col_title:
        st.markdown(f"""
        <div class="main-header" style="text-align: left;">
            <h2>Chat with your {name}</h2>
            <p class="subtitle">Using <strong>{st.session_state.model}</strong> · Stays strictly within {name} topics</p>
        </div>
        """, unsafe_allow_html=True)

    with col_download:
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        current_history = st.session_state.messages.setdefault(st.session_state.personality, [])
        chat_json = json.dumps(current_history, indent=2)
        st.download_button(
            label="Download Chat",
            data=chat_json,
            file_name=f"{name.lower().replace(' ', '_')}_chat.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown(f'<div class="gradient-divider" style="background: {p["gradient"]};"></div>', unsafe_allow_html=True)


def render_suggested_prompts():
    """Show clickable prompt suggestions when current personality chat is empty."""
    current_history = st.session_state.messages.setdefault(st.session_state.personality, [])
    if current_history:
        return

    p       = PERSONALITIES[st.session_state.personality]
    prompts = p["suggested_prompts"]

    st.markdown('<div class="suggested-label">Try asking...</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    for i, prompt in enumerate(prompts):
        col = col1 if i % 2 == 0 else col2
        with col:
            if st.button(prompt, key=f"sugg_{i}_{st.session_state.personality}"):
                st.session_state.pending_prompt = prompt
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)


def render_chat_history():
    current_history = st.session_state.messages.setdefault(st.session_state.personality, [])
    for msg in current_history:
        role    = msg["role"]
        content = msg["content"]

        with st.chat_message(role):
            st.markdown(content)


def call_groq(client: Groq, system_prompt: str, messages: list, model: str) -> tuple[str, int]:
    api_messages = [{"role": "system", "content": system_prompt}] + messages

    try:
        response = client.chat.completions.create(
            model    = model,
            messages = api_messages,
            temperature = 0.7,
            max_tokens  = 1024,
        )

        reply  = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage else 0
        return reply, tokens

    except Exception as e:
        error_msg = str(e)

        if "401" in error_msg or "invalid_api_key" in error_msg.lower():
            return "Invalid API Key. Please check your Groq API key in `.streamlit/secrets.toml`.", 0
        elif "429" in error_msg or "rate_limit" in error_msg.lower():
            return "Rate limit reached. Please wait a moment and try again.", 0
        elif "model_not_found" in error_msg.lower():
            return f"Model `{model}` not found. Please select a different model from the sidebar.", 0
        else:
            return f"API Error: {error_msg}", 0


def process_user_input(user_input: str, client: Groq):
    """Append user message, call Groq, and store reply to re-render cleanly."""
    current_history = st.session_state.messages.setdefault(st.session_state.personality, [])

    # Append user message
    current_history.append({"role": "user", "content": user_input})

    p             = PERSONALITIES[st.session_state.personality]
    system_prompt = p["system_prompt"]

    with st.spinner("Thinking..."):
        reply, tokens = call_groq(
            client        = client,
            system_prompt = system_prompt,
            messages      = current_history,
            model         = st.session_state.model,
        )

    # Append assistant reply
    current_history.append({"role": "assistant", "content": reply})
    st.session_state.total_tokens += tokens
    st.session_state.msg_count    += 1
    st.rerun()


def main():
    init_session_state()
    inject_css(st.session_state.theme)

    client = get_groq_client()

    render_sidebar()

    _, center, _ = st.columns([0.5, 9, 0.5])

    with center:
        render_header()
        render_suggested_prompts()
        render_chat_history()

        # Handle prompt shortcuts
        if st.session_state.pending_prompt:
            pending = st.session_state.pending_prompt
            st.session_state.pending_prompt = None
            process_user_input(pending, client)

        p_name      = st.session_state.personality
        placeholder = f"Ask your {p_name} anything…"

        user_input = st.chat_input(placeholder)

        if user_input and user_input.strip():
            process_user_input(user_input.strip(), client)


if __name__ == "__main__":
    main()