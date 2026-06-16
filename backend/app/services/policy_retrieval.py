import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class PolicyDocument:
    """A lightweight internal policy record used for retrieval."""

    policy_id: str
    title: str
    keywords: tuple[str, ...]
    procedure: str
    escalation: str


@lru_cache
def load_policies() -> tuple[PolicyDocument, ...]:
    """Load the bundled demonstration policy library."""
    policy_path = Path(__file__).resolve().parents[1] / "data" / "policies.json"
    raw_policies = json.loads(policy_path.read_text(encoding="utf-8"))
    return tuple(
        PolicyDocument(
            policy_id=item["id"],
            title=item["title"],
            keywords=tuple(item["keywords"]),
            procedure=item["procedure"],
            escalation=item["escalation"],
        )
        for item in raw_policies
    )


def retrieve_policies(description: str, limit: int = 3) -> list[PolicyDocument]:
    """Return policies ranked by transparent keyword overlap."""
    normalized = description.casefold()
    ranked: list[tuple[int, PolicyDocument]] = []

    for policy in load_policies():
        score = sum(1 for keyword in policy.keywords if keyword.casefold() in normalized)
        if score > 0:
            ranked.append((score, policy))

    ranked.sort(key=lambda item: (-item[0], item[1].policy_id))
    selected = [policy for _, policy in ranked[:limit]]

    if not selected:
        general_policy = next(
            policy for policy in load_policies() if policy.policy_id == "POL-GEN-006"
        )
        selected.append(general_policy)

    return selected


def format_policy_context(policies: list[PolicyDocument]) -> str:
    """Format retrieved policies for inclusion in the Gemini prompt."""
    return "\n\n".join(
        (
            f"Policy ID: {policy.policy_id}\n"
            f"Title: {policy.title}\n"
            f"Procedure: {policy.procedure}\n"
            f"Escalation: {policy.escalation}"
        )
        for policy in policies
    )
