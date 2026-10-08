from decision_platform.telemetry import redact


def test_redacts_nested_secrets() -> None:
    value = {"email": "person@example.com", "nested": {"token": "abc", "safe": 42}}
    assert redact(value) == {
        "email": "[REDACTED]",
        "nested": {"token": "[REDACTED]", "safe": 42},
    }
