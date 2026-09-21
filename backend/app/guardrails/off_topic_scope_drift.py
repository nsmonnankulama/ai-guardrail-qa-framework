import re

from app.guardrails.base import GuardrailResult

_WORD_RE = re.compile(r"[a-zA-Z']+")


def _tokenize(text: str):
    return {w.lower() for w in _WORD_RE.findall(text or "")}


def check(response_text: str, context: dict) -> GuardrailResult:
    allowed_topics = context.get("allowed_topics") or []
    text = response_text or ""

    if not allowed_topics:
        return GuardrailResult(
            passed=True,
            severity="none",
            message="No allowed-topic list configured; scope-drift check skipped.",
        )

    tokens = _tokenize(text)
    if len(tokens) < 4:
        return GuardrailResult(passed=True, severity="none", message="Response too short to assess scope drift.")

    topic_tokens = set()
    for topic in allowed_topics:
        topic_tokens |= _tokenize(topic)

    overlap = tokens & topic_tokens
    if not overlap:
        return GuardrailResult(
            passed=False,
            severity="medium",
            evidence=[text[:200]],
            message=f"Response does not reference any allowed topic ({', '.join(allowed_topics)}).",
        )

    return GuardrailResult(
        passed=True,
        severity="none",
        message=f"Response stays within allowed scope (matched: {', '.join(sorted(overlap))}).",
    )
