"""Sidebar: model selection and generation parameters."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from config.settings import ModelSpec, list_models
from models.provider import GenerationParams


@dataclass(frozen=True)
class SidebarState:
    model: ModelSpec
    params: GenerationParams


def render_sidebar() -> SidebarState:
    models = list_models()
    labels = {m.display_name: m for m in models}

    st.sidebar.header("Modelo")
    selected_label = st.sidebar.selectbox(
        "Selecciona un modelo",
        options=list(labels.keys()),
        index=0,
    )
    model = labels[selected_label]
    defaults = model.defaults

    st.sidebar.header("Parámetros")
    st.sidebar.caption(f"Deployment: `{model.deployment}`")
    st.sidebar.caption(f"API: `{model.api_kind}` · backend: `{model.backend}`")

    reasoning_effort: str | None = defaults.default_reasoning_effort
    if defaults.supports_reasoning_effort and defaults.reasoning_effort_options:
        option_labels = {opt.label: opt.value for opt in defaults.reasoning_effort_options}
        default_label = next(
            (
                opt.label
                for opt in defaults.reasoning_effort_options
                if opt.value == defaults.default_reasoning_effort
            ),
            defaults.reasoning_effort_options[0].label,
        )
        # Reset widget when model changes so options/defaults stay in sync.
        selected_effort_label = st.sidebar.selectbox(
            "Razonamiento",
            options=list(option_labels.keys()),
            index=list(option_labels.keys()).index(default_label),
            key=f"reasoning_effort_{model.id}",
            help="Controla cuánto “piensa” el modelo antes de responder.",
        )
        reasoning_effort = option_labels[selected_effort_label]
    else:
        st.sidebar.caption("Este modelo no expone nivel de razonamiento.")

    temperature: float | None = None
    top_p: float | None = None
    if defaults.supports_temperature:
        temperature = st.sidebar.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=float(defaults.temperature),
            step=0.1,
            key=f"temperature_{model.id}",
        )
    if defaults.supports_top_p:
        top_p = st.sidebar.slider(
            "Top P",
            min_value=0.0,
            max_value=1.0,
            value=float(defaults.top_p),
            step=0.05,
            key=f"top_p_{model.id}",
        )

    max_output_tokens = st.sidebar.number_input(
        "Max output tokens",
        min_value=64,
        max_value=128_000,
        value=int(defaults.max_output_tokens),
        step=64,
        key=f"max_tokens_{model.id}",
    )

    system_prompt = st.sidebar.text_area(
        "System prompt (opcional)",
        value="",
        height=100,
        placeholder="Eres un asistente útil…",
        key=f"system_prompt_{model.id}",
    )

    caps = []
    caps.append("visión" if defaults.supports_vision else "sin visión")
    caps.append("PDF nativo" if defaults.supports_pdf else "PDF como texto")
    st.sidebar.caption("Capacidades: " + " · ".join(caps))

    params = GenerationParams(
        max_output_tokens=int(max_output_tokens),
        system_prompt=system_prompt.strip() or None,
        reasoning_effort=reasoning_effort,
        temperature=temperature,
        top_p=top_p,
    )
    return SidebarState(model=model, params=params)
