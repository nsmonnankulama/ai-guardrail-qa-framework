import datetime
from typing import Optional, List, Any, Dict

from pydantic import BaseModel, ConfigDict


class ConnectorBase(BaseModel):
    name: str
    type: str
    config: Dict[str, Any] = {}


class ConnectorCreate(ConnectorBase):
    pass


class ConnectorOut(ConnectorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime.datetime


class GuardrailPolicyBase(BaseModel):
    name: str
    company_name: str = ""
    product_name: str = ""
    allowed_topics: List[str] = []
    competitor_names: List[str] = []
    banned_words: List[str] = []
    required_disclaimers: List[str] = []


class GuardrailPolicyCreate(GuardrailPolicyBase):
    pass


class GuardrailPolicyOut(GuardrailPolicyBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime.datetime


class TestCaseBase(BaseModel):
    category: str
    prompt: str
    expected_behavior: str = "refuse"
    kb_context: str = ""


class TestCaseCreate(TestCaseBase):
    suite_id: int


class TestCaseOut(TestCaseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    suite_id: int
    created_at: datetime.datetime


class TestCaseGenerateRequest(BaseModel):
    suite_id: int
    category: str
    company_name: str = ""
    product_name: str = ""
    allowed_topics: List[str] = []
    competitor_names: List[str] = []
    count: int = 5


class TestSuiteBase(BaseModel):
    name: str
    description: str = ""
    policy_id: Optional[int] = None


class TestSuiteCreate(TestSuiteBase):
    pass


class TestSuiteOut(TestSuiteBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime.datetime
    test_cases: List[TestCaseOut] = []


class TestCaseResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    test_case_id: int
    category: str
    prompt: str
    response_text: str
    passed: bool
    severity: str
    evidence: List[str]
    message: str
    latency_ms: float
    error: Optional[str] = None
    created_at: datetime.datetime


class TestRunCreate(BaseModel):
    suite_id: int
    connector_id: int


class TestRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    suite_id: int
    connector_id: int
    status: str
    total_count: int
    pass_count: int
    fail_count: int
    started_at: datetime.datetime
    finished_at: Optional[datetime.datetime] = None
    error: Optional[str] = None


class TestRunDetailOut(TestRunOut):
    results: List[TestCaseResultOut] = []


class DashboardStats(BaseModel):
    total_runs: int
    total_cases_executed: int
    pass_rate: float
    category_breakdown: Dict[str, Dict[str, int]]
    recent_runs: List[TestRunOut]
