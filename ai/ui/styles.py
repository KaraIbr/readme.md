"""Minimal visual polish for the Streamlit app."""

from __future__ import annotations

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
  font-family: "IBM Plex Sans", sans-serif;
}

.block-container {
  padding-top: 2rem;
  max-width: 960px;
}

h1, h2, h3 {
  font-family: "IBM Plex Sans", sans-serif;
  letter-spacing: -0.02em;
}

div[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #f3f5f7 0%, #e8edf2 100%);
}

textarea, .stTextInput input {
  font-family: "IBM Plex Mono", monospace !important;
}
</style>
"""


def inject_styles() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
