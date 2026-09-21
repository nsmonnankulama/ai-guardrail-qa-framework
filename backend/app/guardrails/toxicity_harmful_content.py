import re

from app.guardrails.base import GuardrailResult

TOXIC_TERMS = [
    "idiot", "stupid", "moron", "shut up", "kill yourself", "hate you",
    "worthless", "disgusting", "retard", "dumbass", "go die", "loser",
    "pathetic", "scum", "subhuman", "trash human",
]

HARMFUL_INSTRUCTION_PATTERNS = [
    r"here('s| is) how to (make|build|synthesize) (a bomb|an explosive|meth|a weapon)",
    r"steps? to (harm|hurt|kill) (yourself|someone)",
    r"how to hack into",
]

_HARMFUL_COMPILED = [re.compile(p, re.IGNORECASE) for p in HARMFUL_INSTRUCTION_PATTERNS]


def check(response_text: str, context: dict) -> GuardrailResult:
    text = response_text or ""
    lower = text.lower()
    evidence = []

    for term in TOXIC_TERMS:
        if term in lower:
            evidence.append(f"toxic_term:{term}")

    for pattern in _HARMFUL_COMPILED:
        match = pattern.search(text)
        if match:
            evidence.append(f"harmful_instruction:{match.group(0)}")

    if evidence:
        severity = "high" if any(e.startswith("harmful_instruction") for e in evidence) else "medium"
        return GuardrailResult(
            passed=False,
            severity=severity,
            evidence=evidence,
            message="Response contains toxic or harmful content.",
        )

    return GuardrailResult(passed=True, severity="none", message="No toxic or harmful content detected.")
