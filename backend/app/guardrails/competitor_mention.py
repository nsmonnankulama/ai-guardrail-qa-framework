import re

from app.guardrails.base import GuardrailResult

ENDORSEMENT_TEMPLATES = [
    r"{name} (is|seems|would be|looks)( \w+){{0,2}} (better|superior|the better choice|a better choice|the way to go)",
    r"(switch|migrate|move) to {name}",
    r"(choose|pick|recommend|go with) {name}( instead)?( over)?",
    r"{name} outperforms",
]


def check(response_text: str, context: dict) -> GuardrailResult:
    text = response_text or ""
    competitor_names = context.get("competitor_names") or []

    if not competitor_names:
        return GuardrailResult(
            passed=True,
            severity="none",
            message="No competitor list configured; competitor-mention check skipped.",
        )

    evidence = []
    for name in competitor_names:
        if not name:
            continue
        escaped = re.escape(name)
        for template in ENDORSEMENT_TEMPLATES:
            pattern = re.compile(template.format(name=escaped), re.IGNORECASE)
            match = pattern.search(text)
            if match:
                evidence.append(f"endorsement:{match.group(0)}")

    if evidence:
        return GuardrailResult(
            passed=False,
            severity="medium",
            evidence=evidence,
            message="Response inappropriately endorses or recommends switching to a competitor.",
        )

    return GuardrailResult(
        passed=True,
        severity="none",
        message="No inappropriate competitor endorsement found (neutral mentions are allowed).",
    )
