"""Streamlit entrypoint for comparing Azure-hosted LLMs."""

from __future__ import annotations

import streamlit as st
from ui.sidebar import render_sidebar
from ui.styles import inject_styles

from documents.attachments import prepare_attachment
from models.registry import get_provider

ACCEPTED_TYPES = ["pdf", "png", "jpg", "jpeg", "webp", "gif"]


def main() -> None:
    st.set_page_config(
        page_title="Model Test",
        layout="centered",
    )
    inject_styles()

    st.title("Model Test")
    st.caption("Prueba y compara modelos LLM hospedados en Azure Foundry.")

    state = render_sidebar()

    uploaded = st.file_uploader(
        "Documento u imagen (opcional)",
        type=ACCEPTED_TYPES,
        accept_multiple_files=False,
        help=(
            "PDF o imagen (PNG, JPEG, WEBP, GIF). "
            "Se envía al modelo de forma nativa cuando es posible."
        ),
    )

    prompt = st.text_area(
        "Prompt",
        height=180,
        placeholder="Escribe tu prompt…",
    )

    run = st.button("Enviar", type="primary", use_container_width=True)

    if not run:
        return

    if not prompt.strip():
        st.warning("Escribe un prompt antes de enviar.")
        return

    attachments = []
    if uploaded is not None:
        try:
            attachments.append(
                prepare_attachment(
                    filename=uploaded.name,
                    data=uploaded.getvalue(),
                    mime_type=uploaded.type,
                )
            )
        except ValueError as exc:
            st.error(str(exc))
            return

    with st.spinner(f"Consultando {state.model.display_name}…"):
        try:
            provider = get_provider(state.model.id)
            result = provider.generate(
                prompt=prompt.strip(),
                params=state.params,
                attachments=attachments,
            )
        except Exception as exc:  # noqa: BLE001 — show any Azure/SDK error in UI
            st.error(f"Error al llamar al modelo: {exc}")
            return

    for warning in result.warnings:
        st.warning(warning)

    st.subheader("Respuesta")
    st.markdown(result.text)
    st.caption(f"Modelo reportado: `{result.model}`")


if __name__ == "__main__":
    main()
