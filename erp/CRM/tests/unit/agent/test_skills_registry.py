from agent.skills.registry import load_skills, select_skills


def test_load_skills_requires_basic_runtime_skills() -> None:
    names = {skill.name for skill in load_skills()}

    assert {
        "crm-entity-resolution",
        "crm-proposal-qa",
        "crm-sales-metrics",
        "crm-pipeline-analysis",
        "crm-operations",
    }.issubset(names)


def test_select_skills_uses_message_keywords() -> None:
    selected = [
        skill.name
        for skill in select_skills("Qué precio por kW tiene la propuesta y qué inversor incluye?")
    ]

    assert selected == [
        "crm-entity-resolution",
        "crm-proposal-qa",
        "crm-sales-metrics",
    ]
