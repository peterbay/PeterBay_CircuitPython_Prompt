# SPDX-FileCopyrightText: Copyright (c) 2023 Petr Vavrin / pvavrin@gmail.com
#
# SPDX-License-Identifier: MIT


class Validator:
    def _check_allowed_types(
        self, allowed_types: dict, input_value: str, value: str
    ) -> tuple:
        if "bool" in allowed_types:
            value_lower = value.lower()
            if value_lower in ["true", "1", "yes", "y"]:
                return True, True, None

            elif value_lower in ["false", "0", "no", "n"]:
                return True, False, None

            return False, input_value, "invalid value"

        if "float" in allowed_types:
            try:
                return True, float(value), None
            except ValueError:
                pass

        if "int" in allowed_types:
            try:
                return True, int(value), None
            except ValueError:
                pass

        if "str" in allowed_types:
            try:
                return True, str(input_value), None
            except ValueError:
                pass

        return False, input_value, "invalid type"

    def _check_rules(self, rules: dict, input_value: str) -> tuple:
        value = input_value if "no_strip" in rules else input_value.strip()

        if "min_length" in rules:
            if len(value) < rules["min_length"]:
                return False, input_value, "too short"

        if "max_length" in rules:
            if len(value) > rules["max_length"]:
                return False, input_value, "too long"

        if "allowed_chars" in rules:
            for char in value:
                if not char in rules["allowed_chars"]:
                    return False, input_value, "invalid character"

        if "allowed_values" in rules:
            if not value in rules["allowed_values"]:
                return False, input_value, "value not allowed"

        if "allowed_types" in rules:
            return self._check_allowed_types(rules["allowed_types"], input_value, value)

        if "regex" in rules:
            import re

            if not re.match(rules["regex"], value):
                return False, input_value, "regex not matched"

        return True, input_value, None

    def validate(self, rules: dict, value: str) -> tuple:
        assert isinstance(rules, dict), "rules must be a dict"

        return self._check_rules(rules, value)
