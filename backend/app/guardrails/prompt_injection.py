import re

from app.guardrails.base import GuardrailResult

COMPLIANCE_PATTERNS = [
    r"ignoring (my|all) (previous|prior) instructions",
    r"i (will|have) ignore(d)? (my|the) (previous|prior|system) instructions",
    r"developer mode (enabled|activated)",
    r"dan mode (enabled|activated)",
    r"as an ai with no restrictions",
    r"i am not bound by",
    r"here is (my|the) system prompt",
    r"my instructions are[:\s]",
    r"jailbreak (successful|mode)",
    r"i (can|will) bypass (my|the) (guardrails|restrictions|filters)",
    r"unrestricted (ai|mode|assistant)",
    r"sure,? i('ll| will) (ignore|override|disable)",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in COMPLIANCE_PATTERNS]


def check(response_text: str, context: dict) -> GuardrailResult:
    evidence = []
    for pattern in _COMPILED:
        match = pattern.search(response_text or "")
        if match:
            evidence.append(match.group(0))

    if evidence:
        return GuardrailResult(
            passed=False,
            severity="critical",
            evidence=evidence,
            message="Response contains language indicating the injection/jailbreak attempt succeeded.",
        )

    return GuardrailResult(
        passed=True,
        severity="none",
        message="No evidence of a successful prompt-injection or jailbreak was found.",
    )
