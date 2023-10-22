# SPDX-FileCopyrightText: Copyright (c) 2023 Petr Vavrin / pvavrin@gmail.com
#
# SPDX-License-Identifier: MIT

from .prompt import Prompt


class Value(Prompt):
    _rules = {}
    _boolean_true = "yes"
    _boolean_false = "no"

    def __init__(self, serial: object) -> None:
        super().__init__(serial)

    def _check_allowed_types(self, allowed_types, value, stripped_value):
        if "bool" in allowed_types:
            lower_value = stripped_value.lower()

            if lower_value in ["true", "1", "yes", "y"]:
                return True, True, None

            elif lower_value in ["false", "0", "no", "n"]:
                return True, False, None

        if "int" in allowed_types:
            try:
                return True, int(stripped_value), None
            except ValueError:
                pass

        if "float" in allowed_types:
            try:
                return True, float(stripped_value), None
            except ValueError:
                pass

        if "str" in allowed_types:
            try:
                return True, str(value), None
            except ValueError:
                pass

        allowed_types_str = ", ".join(allowed_types)
        return False, value, f"invalid type - allowed types: {allowed_types_str}"

    def _validate_number(self, value, rules):
        if "min" in rules:
            if value < rules["min"]:
                return False, value, "too small"

        if "max" in rules:
            if value > rules["max"]:
                return False, value, "too big"

        return True, value, None

    def _validate_user_input(self, value, rules):
        if not rules:
            return True, value, None

        stripped_value = value.strip()

        if "min_length" in rules:
            if len(stripped_value) < rules["min_length"]:
                return False, value, "too short"

        if "max_length" in rules:
            if len(stripped_value) > rules["max_length"]:
                return False, value, "too long"

        if "allowed_chars" in rules:
            for char in stripped_value:
                if not char in rules["allowed_chars"]:
                    return False, value, "invalid character"

        if "allowed_values" in rules:
            if not stripped_value in rules["allowed_values"]:
                return False, value, "invalid value"

        if "allowed_types" in rules:
            allowed_types = rules["allowed_types"]
            valid, value, error = self._check_allowed_types(
                allowed_types, value, stripped_value
            )
            if not valid:
                return False, value, error

            if "int" in allowed_types or "float" in allowed_types:
                valid, value, error = self._validate_number(value, rules)
                if not valid:
                    return False, value, error

        return True, value, None

    def set_rules(self, rules: dict) -> None:
        self._rules = rules

    def set_value(self, value: str) -> None:
        if isinstance(value, bool):
            value = self._boolean_true if value else self._boolean_false

        self.set_buffer(value)

    def set_settings(self, settings: dict) -> None:
        if "boolean" in settings:
            if "true" in settings["boolean"]:
                self._boolean_true = settings["boolean"]["true"]

            if "false" in settings["boolean"]:
                self._boolean_false = settings["boolean"]["false"]

    def read_non_blocking(self, prompt_string: str = "> ") -> str:
        result = super().read_non_blocking(prompt_string)
        if result is None:
            return None

        valid, value, error = self._validate_user_input(result, self._rules)
        if valid:
            return value

        self.write_line(error)
        return None
