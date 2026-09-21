from app.guardrails import (
    prompt_injection,
    pii_leakage,
    toxicity_harmful_content,
    off_topic_scope_drift,
    hallucination_factual_grounding,
    refusal_correctness,
    brand_tone_compliance,
    competitor_mention,
)

CATEGORIES = [
    "prompt_injection",
    "pii_leakage",
    "toxicity_harmful_content",
    "off_topic_scope_drift",
    "hallucination_factual_grounding",
    "refusal_correctness",
    "brand_tone_compliance",
    "competitor_mention",
]

_REGISTRY = {
    "prompt_injection": prompt_injection.check,
    "pii_leakage": pii_leakage.check,
    "toxicity_harmful_content": toxicity_harmful_content.check,
    "off_topic_scope_drift": off_topic_scope_drift.check,
    "hallucination_factual_grounding": hallucination_factual_grounding.check,
    "refusal_correctness": refusal_correctness.check,
    "brand_tone_compliance": brand_tone_compliance.check,
    "competitor_mention": competitor_mention.check,
}


def get_checker(category: str):
    checker = _REGISTRY.get(category)
    if checker is None:
        raise ValueError(f"Unknown guardrail category: {category}")
    return checker
