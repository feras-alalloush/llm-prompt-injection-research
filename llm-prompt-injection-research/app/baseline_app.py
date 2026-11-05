"""
Baseline (unprotected) ShopEase e-commerce demo with embedded support chat.

Looks like a normal storefront. Chat is one feature inside the site.
No prompt-injection defenses — research control condition.
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.turn_handler import process_user_turn

load_dotenv(PROJECT_ROOT / ".env")

# Free tier via Groq (OpenAI-compatible API)
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MODEL_NAME = "openai/gpt-oss-20b"
APP_VERSION = "baseline"
# Person 1 Baseline must stay False. Protected app sets this to True.
ENABLE_DEFENSES = False

# Fake catalog / demo data for the mock storefront
PRODUCTS = [
    {
        "name": "Aurora Wireless Headphones",
        "price": "$89.99",
        "tag": "Audio",
        "blurb": "Noise-cancelling over-ear headphones with 30-hour battery.",
    },
    {
        "name": "Nimbus Desk Lamp",
        "price": "$42.50",
        "tag": "Home",
        "blurb": "Adjustable LED lamp with warm and cool light modes.",
    },
    {
        "name": "TrailRunner Pro Sneakers",
        "price": "$119.00",
        "tag": "Footwear",
        "blurb": "Lightweight trainers for daily runs and weekend walks.",
    },
    {
        "name": "Forge Stainless Water Bottle",
        "price": "$28.00",
        "tag": "Outdoor",
        "blurb": "Insulated 750ml bottle — keeps drinks cold for 24 hours.",
    },
]

DEMO_ORDERS = {
    "SE-10428": {
        "status": "Shipped",
        "items": "Aurora Wireless Headphones × 1",
        "eta": "Nov 8, 2026",
        "carrier": "ExpressRoute",
    },
    "SE-10991": {
        "status": "Processing",
        "items": "Nimbus Desk Lamp × 2",
        "eta": "Nov 12, 2026",
        "carrier": "Pending assignment",
    },
    "SE-10003": {
        "status": "Delivered",
        "items": "TrailRunner Pro Sneakers × 1",
        "eta": "Delivered Oct 29, 2026",
        "carrier": "CityParcel",
    },
}

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');

:root {
  --ink: #0b1b2b;
  --muted: #334155;
  --bg: #eef2f0;
  --panel: #ffffff;
  --accent: #0b5f58;
  --accent-soft: #c8ebe5;
  --line: #b8c5bf;
  --warm: #9a3f12;
}

html, body, .stApp {
  font-family: 'DM Sans', sans-serif;
  color: var(--ink);
}

.stApp {
  background: #eef2f0;
}

.stMarkdown p, .stCaption, [data-testid="stCaption"],
.stTextInput label {
  color: var(--ink) !important;
}

.stCaption, [data-testid="stCaption"] {
  color: var(--muted) !important;
  opacity: 1 !important;
  font-weight: 500 !important;
}

/* Chatbot input field — white, no border */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] form,
.stChatInput,
.stChatInput > div,
[data-testid="stChatInput"] *,
[data-testid="stChatInput"]:focus,
[data-testid="stChatInput"]:focus-within,
[data-testid="stChatInput"] > div:focus,
[data-testid="stChatInput"] > div:focus-within {
  background: #ffffff !important;
  background-color: #ffffff !important;
  border: none !important;
  border-color: transparent !important;
  outline: none !important;
  box-shadow: none !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] div[contenteditable="true"],
.stChatInput textarea,
[data-testid="stChatInput"] [data-baseweb="base-input"],
[data-testid="stChatInput"] [data-baseweb="textarea"] {
  color: #0b1b2b !important;
  -webkit-text-fill-color: #0b1b2b !important;
  caret-color: #0b1b2b !important;
  background: #ffffff !important;
  background-color: #ffffff !important;
  border: none !important;
  border-radius: 14px !important;
  outline: none !important;
  box-shadow: none !important;
}

[data-testid="stChatInput"] textarea:focus,
.stChatInput textarea:focus,
[data-testid="stChatInput"]:focus-within {
  background: #ffffff !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
}

[data-testid="stChatInput"] textarea::placeholder,
.stChatInput textarea::placeholder {
  color: #94a3b8 !important;
  -webkit-text-fill-color: #94a3b8 !important;
  opacity: 1 !important;
}

/* Keep surrounding chat input chrome white */
[data-testid="stBottomBlockContainer"],
[data-testid="stChatInputContainer"],
footer[data-testid="stChatInputFooter"],
div[data-testid="stBottom"] {
  background: #f8fafc !important;
  background-color: #f8fafc !important;
}

.stTextInput input,
.stTextInput textarea {
  color: #0b1b2b !important;
  -webkit-text-fill-color: #0b1b2b !important;
  caret-color: #0b1b2b !important;
  background-color: #ffffff !important;
}

.stTextInput input::placeholder {
  color: #64748b !important;
  -webkit-text-fill-color: #64748b !important;
  opacity: 1 !important;
}

#MainMenu, footer, header { visibility: hidden; }

.brand-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.85rem 1.25rem;
  margin-bottom: 1.25rem;
  background: var(--panel);
  border: 1.5px solid var(--line);
  border-radius: 18px;
  box-shadow: 0 8px 24px rgba(11, 27, 43, 0.08);
}

.brand-mark {
  display: flex;
  align-items: baseline;
  gap: 0.55rem;
}

.brand-name {
  font-family: 'Fraunces', serif;
  font-size: 1.85rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  color: var(--ink) !important;
  line-height: 1;
}

.brand-tag {
  font-size: 0.78rem;
  color: #064e47 !important;
  background: var(--accent-soft);
  border: 1px solid #8fcfc6;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-weight: 700;
}

.brand-meta {
  color: var(--muted) !important;
  font-size: 0.92rem;
  font-weight: 600;
  text-align: right;
}

.hero {
  background: linear-gradient(125deg, #0b5f58 0%, #12324a 100%);
  color: #ffffff !important;
  border-radius: 22px;
  padding: 2.1rem 2rem;
  margin-bottom: 1.35rem;
  border: 1px solid #0a4d47;
}

.hero h1 {
  font-family: 'Fraunces', serif;
  font-size: 2.35rem;
  margin: 0 0 0.55rem 0;
  letter-spacing: -0.03em;
  color: #ffffff !important;
}

.hero p {
  margin: 0;
  max-width: 36rem;
  color: #f3faf8 !important;
  opacity: 1;
  font-size: 1.08rem;
  line-height: 1.55;
  font-weight: 500;
}

.section-title {
  font-family: 'Fraunces', serif;
  font-size: 1.5rem;
  margin: 0.4rem 0 0.85rem 0;
  color: var(--ink) !important;
  font-weight: 700;
}

.product-card, .info-card, .order-card {
  background: var(--panel);
  border: 1.5px solid var(--line);
  border-radius: 16px;
  padding: 1.15rem 1.2rem;
  height: 100%;
  color: var(--ink);
}

.product-card p, .info-card p, .order-card p {
  color: var(--muted) !important;
  line-height: 1.5;
}

.product-tag {
  display: inline-block;
  font-size: 0.75rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #064e47 !important;
  background: var(--accent-soft);
  border: 1px solid #8fcfc6;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  margin-bottom: 0.55rem;
  font-weight: 700;
}

.product-name {
  font-weight: 700;
  font-size: 1.08rem;
  margin-bottom: 0.4rem;
  color: var(--ink) !important;
}

.product-price {
  color: var(--warm) !important;
  font-weight: 700;
  margin-top: 0.7rem;
  font-size: 1.05rem;
}

.muted { color: var(--muted) !important; font-weight: 500; }

.chat-shell {
  background: #f8fafc;
  border: 1.5px solid #cbd5e1;
  border-radius: 18px;
  padding: 1rem 1.1rem 1rem 1.1rem;
  min-height: 420px;
}

/* ---- Chat bubbles: high-contrast, readable ---- */
div[data-testid="stChatMessage"] {
  background: #ffffff !important;
  border: 1.5px solid #cbd5e1 !important;
  border-radius: 16px !important;
  padding: 0.85rem 1rem !important;
  margin: 0.55rem 0 !important;
  box-shadow: none !important;
}

/* User messages: soft teal bubble + dark text */
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  background: #dff7f2 !important;
  border-color: #7dcdc2 !important;
}

/* Assistant messages: white bubble + dark text */
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
  background: #ffffff !important;
  border-color: #cbd5e1 !important;
}

div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] *,
div[data-testid="stChatMessage"] [data-testid="stChatMessageContent"],
div[data-testid="stChatMessage"] [data-testid="stChatMessageContent"] *,
div[data-testid="stChatMessage"] p,
div[data-testid="stChatMessage"] li,
div[data-testid="stChatMessage"] ul,
div[data-testid="stChatMessage"] ol,
div[data-testid="stChatMessage"] span,
div[data-testid="stChatMessage"] strong,
div[data-testid="stChatMessage"] em,
div[data-testid="stChatMessage"] a,
div[data-testid="stChatMessage"] code {
  color: #0f172a !important;
  -webkit-text-fill-color: #0f172a !important;
  opacity: 1 !important;
}

div[data-testid="stChatMessage"] ul,
div[data-testid="stChatMessage"] ol {
  margin: 0.4rem 0 0.6rem 1.2rem !important;
}

div[data-testid="stChatMessage"] li {
  margin: 0.25rem 0 !important;
  line-height: 1.55 !important;
}

.latency-pill {
  display: inline-block;
  margin-top: 0.45rem;
  font-size: 0.78rem;
  color: #0f172a !important;
  -webkit-text-fill-color: #0f172a !important;
  background: #e2e8f0;
  border: 1px solid #94a3b8;
  padding: 0.18rem 0.6rem;
  border-radius: 999px;
  font-weight: 700;
}

section[data-testid="stSidebar"] {
  background: #102536 !important;
  border-right: none;
}

section[data-testid="stSidebar"] > div {
  padding-top: 1.1rem;
}

section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] [data-testid="stCaption"],
section[data-testid="stSidebar"] .stCaption {
  color: #e8eef4 !important;
}

.sidebar-brand {
  font-family: 'Fraunces', serif;
  font-size: 1.55rem;
  font-weight: 700;
  color: #ffffff !important;
  letter-spacing: -0.02em;
  margin-bottom: 0.15rem;
}

.sidebar-sub {
  color: #9fb2c3 !important;
  font-size: 0.82rem;
  margin-bottom: 1rem;
}

.nav-hint {
  color: #9fb2c3 !important;
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 700;
  margin: 0.4rem 0 0.65rem 0;
}

section[data-testid="stSidebar"] div.stButton > button {
  width: 100%;
  justify-content: flex-start;
  border-radius: 12px;
  border: 1px solid transparent;
  background: transparent;
  color: #d7e2ec !important;
  font-weight: 600;
  padding: 0.65rem 0.85rem;
  margin-bottom: 0.35rem;
}

section[data-testid="stSidebar"] div.stButton > button:hover {
  background: #1a3a52 !important;
  border-color: #2a516e;
  color: #ffffff !important;
}

section[data-testid="stSidebar"] div.stButton > button[kind="primary"],
section[data-testid="stSidebar"] div.stButton > button[data-testid="baseButton-primary"] {
  background: #0f766e !important;
  border-color: #0f766e !important;
  color: #ffffff !important;
}

.sidebar-card {
  background: #18344a;
  border: 1px solid #2a516e;
  border-radius: 14px;
  padding: 0.85rem 0.95rem;
  margin-top: 0.85rem;
  color: #e8eef4 !important;
}

.sidebar-card strong {
  color: #ffffff !important;
}
</style>
"""


def get_llm_client() -> OpenAI:
    """Create a Groq client using the free OpenAI-compatible endpoint."""
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError(
            "GROQ_API_KEY is missing. Add it to the .env file "
            "(get a free key from https://console.groq.com/keys)."
        )
    return OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)


def init_session_state() -> None:
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "page" not in st.session_state:
        st.session_state.page = "Home"
    if "order_query" not in st.session_state:
        st.session_state.order_query = ""


def render_brand_bar() -> None:
    st.markdown(
        """
        <div class="brand-bar">
          <div class="brand-mark">
            <div class="brand-name">ShopEase</div>
            <div class="brand-tag">demo store</div>
          </div>
          <div class="brand-meta">Free shipping over $50 · Easy 30-day returns</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home() -> None:
    st.markdown(
        """
        <div class="hero">
          <h1>Everything you need, delivered with ease.</h1>
          <p>
            Browse featured products, track a demo order, review return policy,
            or talk to our support assistant — all inside this mock storefront.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="info-card">
              <div class="product-tag">Catalog</div>
              <div class="product-name">Browse products</div>
              <p class="muted">See sample items customers ask about in support chats.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="info-card">
              <div class="product-tag">Orders</div>
              <div class="product-name">Track a shipment</div>
              <p class="muted">Try demo IDs like SE-10428 or SE-10991.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="info-card">
              <div class="product-tag">Support</div>
              <div class="product-name">Live assistant</div>
              <p class="muted">Open Live Chat for help with orders, returns, and products.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_products() -> None:
    st.markdown('<div class="section-title">Featured products</div>', unsafe_allow_html=True)
    st.caption("Fictional catalog used by the support assistant for product questions.")

    rows = [PRODUCTS[:2], PRODUCTS[2:]]
    for row in rows:
        cols = st.columns(2)
        for col, product in zip(cols, row):
            with col:
                st.markdown(
                    f"""
                    <div class="product-card">
                      <div class="product-tag">{product["tag"]}</div>
                      <div class="product-name">{product["name"]}</div>
                      <p class="muted">{product["blurb"]}</p>
                      <div class="product-price">{product["price"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.button(
                    "Add to cart (demo)",
                    key=f"cart_{product['name']}",
                    use_container_width=True,
                    disabled=True,
                )


def render_orders() -> None:
    st.markdown('<div class="section-title">Order tracking</div>', unsafe_allow_html=True)
    st.caption("Demo only — no real orders are stored. Try SE-10428, SE-10991, or SE-10003.")

    order_id = st.text_input(
        "Order number",
        value=st.session_state.order_query,
        placeholder="e.g. SE-10428",
    ).strip().upper()
    st.session_state.order_query = order_id

    if st.button("Track order", type="primary"):
        if order_id in DEMO_ORDERS:
            order = DEMO_ORDERS[order_id]
            st.markdown(
                f"""
                <div class="order-card">
                  <div class="product-tag">Order {order_id}</div>
                  <div class="product-name">Status: {order["status"]}</div>
                  <p class="muted"><strong>Items:</strong> {order["items"]}</p>
                  <p class="muted"><strong>ETA:</strong> {order["eta"]}</p>
                  <p class="muted"><strong>Carrier:</strong> {order["carrier"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif order_id:
            st.warning("Order not found in the demo dataset. Try SE-10428.")
        else:
            st.info("Enter a demo order number first.")


def render_returns() -> None:
    st.markdown('<div class="section-title">Returns & refunds</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="info-card">
          <p><strong>Return window:</strong> 30 days from delivery for unused items in original packaging.</p>
          <p><strong>Refund timing:</strong> 5–7 business days after the warehouse receives the return.</p>
          <p><strong>Exclusions:</strong> gift cards, personalized items, and final-sale clearances.</p>
          <p class="muted">Need help starting a return? Open <strong>Live Chat</strong> and ask the assistant.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def handle_chat_turn(user_input: str) -> None:
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        client = get_llm_client()
        outcome = process_user_turn(
            user_input=user_input,
            history=st.session_state.messages,
            client=client,
            model_name=MODEL_NAME,
            session_id=st.session_state.session_id,
            app_version=APP_VERSION,
            enable_defenses=ENABLE_DEFENSES,
        )
    except Exception as exc:  # noqa: BLE001
        outcome_text = (
            "Sorry, I could not process your request due to a configuration "
            f"or API error: {exc}"
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": outcome_text, "latency_ms": 0.0}
        )
        return

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": outcome.assistant_text,
            "latency_ms": outcome.latency_ms,
            "blocked": outcome.blocked,
        }
    )


def render_live_chat() -> None:
    st.markdown('<div class="section-title">Live support chat</div>', unsafe_allow_html=True)
    st.caption(
        "ShopEase assistant can help with order inquiries, return policies, and product details."
    )

    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.write(
                "Hi! Welcome to ShopEase support. "
                "Ask me about products, order status, or returns."
            )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Plain text avoids low-contrast markdown list styling
            st.write(message["content"])
            if message["role"] == "assistant" and "latency_ms" in message:
                st.caption(f"Latency: {message['latency_ms']:.2f} ms")

    user_input = st.chat_input("Ask about orders, returns, or products…")
    if user_input:
        handle_chat_turn(user_input)
        st.rerun()


def main() -> None:
    st.set_page_config(
        page_title="ShopEase — Online Store",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    init_session_state()

    nav_items = [
        ("Home", "Home"),
        ("Products", "Products"),
        ("Orders", "Track order"),
        ("Returns", "Returns"),
        ("Live Chat", "Live chat"),
    ]

    with st.sidebar:
        st.markdown('<div class="sidebar-brand">ShopEase</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sidebar-sub">Customer portal · demo</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="nav-hint">Menu</div>', unsafe_allow_html=True)

        for key, label in nav_items:
            is_active = st.session_state.page == key
            if st.button(
                label,
                key=f"nav_{key}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state.page = key
                st.rerun()

        mode_label = (
            "Protected · defenses ON"
            if ENABLE_DEFENSES
            else "Baseline · unprotected chat"
        )
        st.markdown(
            f"""
            <div class="sidebar-card">
              <strong>Guest shopper</strong><br/>
              Cart: 0 items<br/>
              <span style="color:#9fb2c3;font-size:0.8rem;">{mode_label}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_brand_bar()

    page = st.session_state.page
    if page == "Home":
        render_home()
    elif page == "Products":
        render_products()
    elif page == "Orders":
        render_orders()
    elif page == "Returns":
        render_returns()
    else:
        render_live_chat()


if __name__ == "__main__":
    main()
