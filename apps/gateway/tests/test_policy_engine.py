import pytest
from apps.gateway.policy_engine import evaluate_dsl

def test_evaluate_dsl_simple():
    rule = {"field": "arguments.amount", "operator": "greater_than", "value": 1000}
    assert evaluate_dsl(rule, {"arguments": {"amount": 1500}}) is True
    assert evaluate_dsl(rule, {"arguments": {"amount": 500}}) is False

def test_evaluate_dsl_nested():
    rule = {
        "condition": "AND",
        "rules": [
            {"field": "arguments.query", "operator": "not_contains", "value": "DROP"},
            {"field": "arguments.table", "operator": "equals", "value": "users"}
        ]
    }
    assert evaluate_dsl(rule, {"arguments": {"query": "SELECT * FROM users", "table": "users"}}) is True
    assert evaluate_dsl(rule, {"arguments": {"query": "DROP TABLE users", "table": "users"}}) is False
