import re

from app.guardrails.base import GuardrailResult

_NUMBER_RE = re.compile(r"\$?\d[\d,]*(?:\.\d+)?%?")


def check(response_text: str, context: dict) -> GuardrailResult:
    kb_context = context.get("kb_context") or ""
    text = response_text or ""

    if not kb_context.strip():
        return GuardrailResult(
            passed=True,
            severity="none",
            message="No knowledge-base context supplied; grounding check skipped.",
        )

    response_numbers = set(_NUMBER_RE.findall(text))
    kb_numbers = set(_NUMBER_RE.findall(kb_context))

    ungrounded = {n for n in response_numbers if n not in kb_numbers}
    ungrounded = {n for n in ungrounded if re.sub(r"[^\d]", "", n)}

    if ungrounded:
        return GuardrailResult(
            passed=False,
            severity="high",
            evidence=sorted(ungrounded),
            message="Response cites figures not present in the supplied knowledge-base context (possible hallucination).",
        )

    return GuardrailResult(
        passed=True,
        severity="none",
        message="Response claims are consistent with the supplied knowledge-base context.",
    )
