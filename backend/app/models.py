import datetime
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    Float,
    ForeignKey,
    JSON,
    Enum,
)
from sqlalchemy.orm import relationship

from app.database import Base


class ConnectorType(str, enum.Enum):
    HTTP = "http"
    LLM = "llm"


class RunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Connector(Base):
    __tablename__ = "connectors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(ConnectorType), nullable=False)
    config = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    runs = relationship("TestRun", back_populates="connector")


class GuardrailPolicy(Base):
    __tablename__ = "guardrail_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    company_name = Column(String, default="")
    product_name = Column(String, default="")
    allowed_topics = Column(JSON, default=list)
    competitor_names = Column(JSON, default=list)
    banned_words = Column(JSON, default=list)
    required_disclaimers = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    suites = relationship("TestSuite", back_populates="policy")


class TestSuite(Base):
    __tablename__ = "test_suites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    policy_id = Column(Integer, ForeignKey("guardrail_policies.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    policy = relationship("GuardrailPolicy", back_populates="suites")
    test_cases = relationship(
        "TestCase", back_populates="suite", cascade="all, delete-orphan"
    )
    runs = relationship("TestRun", back_populates="suite")


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    suite_id = Column(Integer, ForeignKey("test_suites.id"), nullable=False)
    category = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    expected_behavior = Column(String, default="refuse")
    kb_context = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    suite = relationship("TestSuite", back_populates="test_cases")
    results = relationship("TestCaseResult", back_populates="test_case")


class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, index=True)
    suite_id = Column(Integer, ForeignKey("test_suites.id"), nullable=False)
    connector_id = Column(Integer, ForeignKey("connectors.id"), nullable=False)
    status = Column(Enum(RunStatus), default=RunStatus.PENDING)
    total_count = Column(Integer, default=0)
    pass_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)

    suite = relationship("TestSuite", back_populates="runs")
    connector = relationship("Connector", back_populates="runs")
    results = relationship(
        "TestCaseResult", back_populates="run", cascade="all, delete-orphan"
    )


class TestCaseResult(Base):
    __tablename__ = "test_case_results"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    category = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    response_text = Column(Text, default="")
    passed = Column(Boolean, default=False)
    severity = Column(String, default="none")
    evidence = Column(JSON, default=list)
    message = Column(Text, default="")
    latency_ms = Column(Float, default=0.0)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    run = relationship("TestRun", back_populates="results")
    test_case = relationship("TestCase", back_populates="results")
