"""Load and select runtime SKILL.md bundles."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class AgentSkill:
    """Runtime skill metadata and instructions."""

    name: str
    description: str
    instructions: str
    path: Path


def _parse_skill(path: Path) -> AgentSkill:
    content = path.read_text(encoding="utf-8")
    metadata: dict[str, str] = {}
    body = content
    if content.startswith("---"):
        _, frontmatter, body = content.split("---", 2)
        for line in frontmatter.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip('"')

    name = metadata.get("name")
    description = metadata.get("description")
    if not name or not description:
        raise ValueError(f"Skill {path} must define name and description")

    return AgentSkill(
        name=name,
        description=description,
        instructions=body.strip(),
        path=path,
    )


@lru_cache
def load_skills() -> tuple[AgentSkill, ...]:
    """Load all runtime skills from the package skills directory."""

    skills_root = Path(__file__).parent
    skill_paths = sorted(skills_root.glob("*/SKILL.md"))
    return tuple(_parse_skill(path) for path in skill_paths)


def select_skills(message: str) -> list[AgentSkill]:
    """Select a small set of skills for a user message."""

    normalized = message.lower()
    skills_by_name = {skill.name: skill for skill in load_skills()}
    selected: list[AgentSkill] = []

    def add(name: str) -> None:
        skill = skills_by_name.get(name)
        if skill is not None and skill not in selected:
            selected.append(skill)

    add("crm-entity-resolution")

    if any(
        keyword in normalized
        for keyword in (
            "proposal",
            "propuesta",
            "propuestas",
            "inverter",
            "inversor",
            "panel",
            "battery",
            "batería",
            "bateria",
            "kw",
            "kwh",
            "potencia",
        )
    ):
        add("crm-proposal-qa")

    if any(
        keyword in normalized
        for keyword in (
            "price",
            "precio",
            "cost",
            "costo",
            "margin",
            "margen",
            "total",
            "budget",
            "presupuesto",
            "por kw",
            "unitario",
        )
    ):
        add("crm-sales-metrics")

    if any(
        keyword in normalized
        for keyword in (
            "stage",
            "etapa",
            "estado",
            "pipeline",
            "transition",
            "transición",
            "transicion",
            "elapsed",
            "tiempo",
            "días",
            "dias",
        )
    ):
        add("crm-pipeline-analysis")

    if any(
        keyword in normalized
        for keyword in (
            "actualiza",
            "actualizar",
            "cambia",
            "cambiar",
            "crea",
            "crear",
            "mueve",
            "mover",
            "marca",
            "marcar",
        )
    ):
        add("crm-operations")

    if len(selected) == 1:
        add("crm-proposal-qa")

    return selected
