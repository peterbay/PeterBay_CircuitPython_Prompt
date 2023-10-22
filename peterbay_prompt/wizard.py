# SPDX-FileCopyrightText: Copyright (c) 2023 Petr Vavrin / pvavrin@gmail.com
#
# SPDX-License-Identifier: MIT

from .serial_io import SerialIO
from .single_select import SingleSelect
from .value import Value


class Wizard(SerialIO):
    def __init__(self, serial: object) -> None:
        super().__init__(serial)
        self._wizard_config = []
        self._single_select = SingleSelect(serial)
        self._value = Value(serial)
        self._default_values = {}
        self.reset()

    def set_config(self, wizard_info: str, wizard_config: list = None) -> None:
        self._wizard_info = wizard_info
        self._wizard_config = wizard_config
        self.reset()

    def set_default_values(self, default_values: dict) -> None:
        self._default_values = default_values

    def reset(self) -> None:
        self._printed_index = None
        self._active_component = None
        self._results = {}

    def _print_wizard_info(self) -> None:
        if self._wizard_info:
            self.write_line(self._wizard_info)

    def _init_wizard_question(self) -> None:
        if self._printed_index is None:
            self._printed_index = 0

        entry = self._wizard_config[self._printed_index]

        question = entry["question"]
        type = entry["type"]
        name = entry["name"]
        data = entry["data"] if "data" in entry else None
        default = entry["default"] if "default" in entry else ""
        settings = entry["settings"] if "settings" in entry else {}

        if name in self._default_values:
            default = self._default_values[name]

        self.write_line(question)

        if type == "single_select":
            self._active_component = self._single_select
            self._single_select.set_options(data)
            if default:
                self._single_select.set_active_option(default)

        elif type == "value":
            rules = entry["rules"] if "rules" in entry else {}
            self._active_component = self._value
            self._value.set_rules(rules)
            self._value.set_value(default)
            self._value.set_settings(settings)

        else:
            raise ValueError(f"Wizard: invalid type: {type}")

    def _set_value(self, value: str) -> None:
        entry = self._wizard_config[self._printed_index]
        self._results[entry["name"]] = value

    def _next_question(self) -> None:
        if len(self._wizard_config) <= self._printed_index + 1:
            return False

        self._printed_index += 1
        self._active_component = None
        self._init_wizard_question()
        return True

    def keyboard_interrupt(self) -> None:
        if self._active_component is not None:
            if hasattr(self._active_component, "keyboard_interrupt"):
                self._active_component.keyboard_interrupt()

    def read_non_blocking(self) -> None:
        if self._printed_index is None:
            self._print_wizard_info()
            self._init_wizard_question()

        if self._active_component is not None:
            result = self._active_component.read_non_blocking()
            if result is not None:
                self._set_value(result)

                next_question = self._next_question()
                if not next_question:
                    return self._results

                return None
