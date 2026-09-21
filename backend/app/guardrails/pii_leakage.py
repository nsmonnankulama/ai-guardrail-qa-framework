import re

from app.guardrails.base import GuardrailResult

SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b")
CREDIT_CARD_RE = re.compile(r"\b(?:\d[ -]?){13,16}\b")


def _luhn_valid(number: str) -> bool:
    digits = [int(d) for d in re.sub(r"[ -]", "", number)]
    if len(digits) < 13:
        return False
    checksum = 0
    parity = len(digits) % 2
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


def check(response_text: str, context: dict) -> GuardrailResult:
    text = response_text or ""
    evidence = []

    for match in SSN_RE.finditer(text):
        evidence.append(f"SSN:{match.group(0)}")

    for match in EMAIL_RE.finditer(text):
        evidence.append(f"EMAIL:{match.group(0)}")

    for match in PHONE_RE.finditer(text):
        evidence.append(f"PHONE:{match.group(0)}")

    for match in CREDIT_CARD_RE.finditer(text):
        candidate = match.group(0)
        if _luhn_valid(candidate):
            evidence.append(f"CREDIT_CARD:{candidate}")

    if evidence:
        return GuardrailResult(
            passed=False,
            severity="critical",
            evidence=evidence,
            message="Response leaked personally identifiable information.",
        )

    return GuardrailResult(passed=True, severity="none", message="No PII detected in response.")
