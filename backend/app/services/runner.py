import datetime

from sqlalchemy.orm import Session

from app import models
from app.connectors.factory import build_connector
from app.guardrails.registry import get_checker


def run_suite(db: Session, suite: models.TestSuite, connector: models.Connector) -> models.TestRun:
    run = models.TestRun(
        suite_id=suite.id,
        connector_id=connector.id,
        status=models.RunStatus.RUNNING,
        total_count=len(suite.test_cases),
        started_at=datetime.datetime.utcnow(),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    policy = suite.policy
    guardrail_context_base = {
        "allowed_topics": policy.allowed_topics if policy else [],
        "competitor_names": policy.competitor_names if policy else [],
        "banned_words": policy.banned_words if policy else [],
        "required_disclaimers": policy.required_disclaimers if policy else [],
    }

    conn_instance = build_connector(connector.type.value if hasattr(connector.type, "value") else connector.type, connector.config)

    pass_count = 0
    fail_count = 0

    try:
        for case in suite.test_cases:
            conn_response = conn_instance.send(case.prompt)

            context = dict(guardrail_context_base)
            context["expected_behavior"] = case.expected_behavior
            context["kb_context"] = case.kb_context

            if conn_response.error:
                result = models.TestCaseResult(
                    run_id=run.id,
                    test_case_id=case.id,
                    category=case.category,
                    prompt=case.prompt,
                    response_text="",
                    passed=False,
                    severity="high",
                    evidence=[],
                    message=f"Connector error: {conn_response.error}",
                    latency_ms=conn_response.latency_ms,
                    error=conn_response.error,
                )
                fail_count += 1
            else:
                checker = get_checker(case.category)
                guardrail_result = checker(conn_response.response_text, context)
                result = models.TestCaseResult(
                    run_id=run.id,
                    test_case_id=case.id,
                    category=case.category,
                    prompt=case.prompt,
                    response_text=conn_response.response_text,
                    passed=guardrail_result.passed,
                    severity=guardrail_result.severity,
                    evidence=guardrail_result.evidence,
                    message=guardrail_result.message,
                    latency_ms=conn_response.latency_ms,
                )
                if guardrail_result.passed:
                    pass_count += 1
                else:
                    fail_count += 1

            db.add(result)

        run.status = models.RunStatus.COMPLETED
        run.pass_count = pass_count
        run.fail_count = fail_count
        run.finished_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(run)
    except Exception as exc:
        run.status = models.RunStatus.FAILED
        run.error = str(exc)
        run.finished_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(run)
        raise

    return run
