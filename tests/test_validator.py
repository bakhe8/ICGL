"""
Tests for the Schema Validator module.
"""

import pytest
from icgl.validator import (
    SchemaValidator,
    ValidationError,
    MultiValidationError,
    validate_concept,
    validate_policy,
    validate_adr,
)
from icgl.policies.enforcement import PolicyEnforcer
from icgl.kb.knowledge_base import KnowledgeBase
from icgl.kb.schemas import Concept, Policy, ADR, SentinelSignal, HumanDecision


class TestValidateConcept:
    def test_valid_concept(self):
        concept = Concept(
            id="test-concept",
            name="Test",
            definition="A test concept",
            invariants=["Rule 1"],
            anti_patterns=["Bad pattern"],
        )
        errors = validate_concept(concept)
        assert len(errors) == 0

    def test_missing_name(self):
        concept = Concept(
            id="test-concept",
            name="",
            definition="A test concept",
            invariants=["Rule 1"],
            anti_patterns=[],
        )
        errors = validate_concept(concept)
        assert any(e.field == "name" for e in errors)

    def test_empty_invariants(self):
        concept = Concept(
            id="test-concept",
            name="Test",
            definition="A test concept",
            invariants=[],
            anti_patterns=[],
        )
        errors = validate_concept(concept)
        assert any(e.field == "invariants" for e in errors)


class TestValidatePolicy:
    def test_valid_policy(self):
        policy = Policy(
            id="policy-test",
            code="P-TEST-01",
            title="Test Policy",
            rule="Must do X",
            severity="HIGH",
            enforced_by=["Sentinel"],
        )
        errors = validate_policy(policy)
        assert len(errors) == 0

    def test_invalid_code_format(self):
        policy = Policy(
            id="policy-test",
            code="INVALID-CODE",
            title="Test Policy",
            rule="Must do X",
            severity="HIGH",
            enforced_by=["Sentinel"],
        )
        errors = validate_policy(policy)
        assert any(e.field == "code" for e in errors)

    def test_invalid_severity(self):
        policy = Policy(
            id="policy-test",
            code="P-TEST-01",
            title="Test Policy",
            rule="Must do X",
            severity="UNKNOWN",
            enforced_by=["Sentinel"],
        )
        errors = validate_policy(policy)
        assert any(e.field == "severity" for e in errors)


class TestValidateADR:
    def test_valid_adr(self):
        adr = ADR(
            id="ADR-TEST",
            title="Test ADR",
            status="DRAFT",
            context="Some context",
            decision="Some decision",
            consequences=["Result"],
            related_policies=[],
            sentinel_signals=[],
            human_decision_id=None,
        )
        errors = validate_adr(adr)
        assert len(errors) == 0

    def test_invalid_status(self):
        adr = ADR(
            id="ADR-TEST",
            title="Test ADR",
            status="INVALID",
            context="Some context",
            decision="Some decision",
            consequences=[],
            related_policies=[],
            sentinel_signals=[],
            human_decision_id=None,
        )
        errors = validate_adr(adr)
        assert any(e.field == "status" for e in errors)


class TestSchemaValidator:
    def test_raises_on_invalid(self):
        validator = SchemaValidator()
        concept = Concept(
            id="",
            name="",
            definition="",
            invariants=[],
            anti_patterns=[],
        )
        with pytest.raises(MultiValidationError):
            validator.validate(concept)

    def test_is_valid_returns_false(self):
        validator = SchemaValidator()
        concept = Concept(
            id="",
            name="",
            definition="",
            invariants=[],
            anti_patterns=[],
        )
        assert validator.is_valid(concept) is False

    def test_is_valid_returns_true(self):
        validator = SchemaValidator()
        concept = Concept(
            id="valid-id",
            name="Valid Name",
            definition="Valid definition",
            invariants=["Rule"],
            anti_patterns=[],
        )
        assert validator.is_valid(concept) is True


class TestPolicyEnforcer:
    def test_policy_violation_reports_severity(self):
        kb = KnowledgeBase()
        enforcer = PolicyEnforcer(kb)
        adr = ADR(
            id="ADR-TEST",
            title="Uses context as authority",
            status="DRAFT",
            context="Context-driven decision",
            decision="decide based on context and derive from batch",
            consequences=[],
            related_policies=[],
            sentinel_signals=[],
            human_decision_id=None,
        )
        report = enforcer.check_adr_compliance(adr)
        assert report.status == "FAIL"
        assert report.max_severity == "CRITICAL"
