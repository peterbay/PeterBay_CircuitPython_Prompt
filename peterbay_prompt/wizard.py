# SPDX-FileCopyrightText: Copyright (c) 2023 Petr Vavrin / pvavrin@gmail.com
#
# SPDX-License-Identifier: MIT

from .serial_io import SerialIO
from .single_select import SingleSelect
from .multi_select import MultiSelect
from .value import Value


class Wizard(SerialIO):
    def __init__(self, serial: object) -> None:
        super().__init__(serial)
        self._wizard_config = []
        self._single_select = SingleSelect(serial)
        self._multi_select = MultiSelect(serial)
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

    def _init_wizard_entry(self) -> None:
        if self._printed_index is None:
            self._printed_index = 0

        entry = self._wizard_config[self._printed_index]

        label = entry.get("label", "")
        type = entry.get("type", None)
        name = entry.get("name", "")
        data = entry.get("data", None)
        default = entry.get("default", "")
        settings = entry.get("settings", {})

        if name in self._default_values:
            default = self._default_values[name]

        self.write_line(label)

        if type == "single_select":
            self._active_component = self._single_select
            self._single_select.set_options(data)
            if default:
                self._single_select.set_active_option(default)

        elif type == "multi_select":
            self._active_component = self._multi_select
            self._multi_select.set_options(data)
            if default:
                self._multi_select.set_active_options(default)

        elif type == "value":
            rules = entry.get("rules", {})
            self._active_component = self._value
            self._value.set_rules(rules)
            self._value.set_value(default)
            self._value.set_settings(settings)

        else:
            raise ValueError(f"Wizard: invalid type: {type}")

    def _set_value(self, value: str) -> None:
        entry = self._wizard_config[self._printed_index]
        self._results[entry["name"]] = value

    def _next_entry(self) -> None:
        if len(self._wizard_config) <= self._printed_index + 1:
            return False

        self._printed_index += 1
        self._active_component = None
        self._init_wizard_entry()
        return True

    def keyboard_interrupt(self) -> None:
        if self._active_component is not None:
            if hasattr(self._active_component, "keyboard_interrupt"):
                self._active_component.keyboard_interrupt()

    def read_non_blocking(self) -> None:
        if self._printed_index is None:
            self._print_wizard_info()
            self._init_wizard_entry()

        if self._active_component is not None:
            result = self._active_component.read_non_blocking()
            if result is not None:
                self._set_value(result)

                next_label = self._next_entry()
                if not next_label:
                    return self._results

                return None
