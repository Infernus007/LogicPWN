import re
from typing import List
from logicpwn.core.reporter.models import RedactionRule
from logicpwn.core.logging.redactor import SensitiveDataRedactor

class AdvancedRedactor(SensitiveDataRedactor):
    def __init__(self, custom_rules: List[RedactionRule] = None):
        super().__init__()
        self.custom_rules = custom_rules or []

    def redact_string_body(self, content: str) -> str:
        redacted = super().redact_string_body(content)
        for rule in self.custom_rules:
            redacted = re.sub(rule.pattern, rule.replacement, redacted, flags=re.IGNORECASE)
        return redacted 