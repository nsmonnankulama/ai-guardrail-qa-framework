from app.guardrails.base import GuardrailResult


def check(response_text: str, context: dict) -> GuardrailResult:
    text = response_text or ""
    lower = text.lower()
    banned_words = context.get("banned_words") or []
    required_disclaimers = context.get("required_disclaimers") or []

    evidence = []
    for word in banned_words:
        if word and word.lower() in lower:
            evidence.append(f"banned_word:{word}")

    missing_disclaimers = [d for d in required_disclaimers if d and d.lower() not in lower]

    if evidence:
        return GuardrailResult(
            passed=False,
            severity="medium",
            evidence=evidence + [f"missing_disclaimer:{d}" for d in missing_disclaimers],
            message="Response violates brand tone guidelines (banned language detected).",
        )

    if required_disclaimers and missing_disclaimers and len(missing_disclaimers) == len(required_disclaimers):
        return GuardrailResult(
            passed=False,
            severity="low",
            evidence=[f"missing_disclaimer:{d}" for d in missing_disclaimers],
            message="Response is missing required brand disclaimers.",
        )

    return GuardrailResult(passed=True, severity="none", message="Response complies with brand tone guidelines.")
