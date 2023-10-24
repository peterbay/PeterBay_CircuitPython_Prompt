# SPDX-FileCopyrightText: Copyright (c) 2023 Petr Vavrin / pvavrin@gmail.com
#
# SPDX-License-Identifier: MIT

from .input import Input


class MultiSelect(Input):
    _rendered = False
    _options = []
    _active_options = []
    _active_line = None
    _label = None

    def set_label(self, label: str) -> None:
        self._label = label
        self._rendered = False

    def set_options(self, options: list) -> None:
        self._options = options
        self._rendered = False

    def set_active_options(self, option: [str, list]) -> None:
        self._active_options = option
        self._active_line = None
        self._rendered = False

    def _write_option_line(self, index: int, entry: dict, render_label: bool) -> None:
        mark = " "

        if self._active_options is None:
            self._active_options = entry["value"]

        if entry["value"] in self._active_options:
            mark = "x"

        if render_label:
            label = entry["label"]
            self.write(f"\33[G [{mark}] {label}\r\n")
        else:
            self.write(f"\33[G [{mark}]\33[2D")

    def _move_cursor(self, count):
        if count < 0:
            count = abs(count)
            self.write(f"\33[{count}F\33[3G")

        elif count > 0:
            self.write(f"\33[{count}E\33[3G")

    def _render(self) -> None:
        if self._label:
            self.write_line(self._label)

        self._active_line = 0

        for index, option in enumerate(self._options):
            self._write_option_line(index, option, True)

        cursor_pos = self._active_line - len(self._options)
        self._move_cursor(cursor_pos)
        self._rendered = True

    def _process_key(self, type: int, key: str) -> bool:
        len_options = len(self._options)
        can_move_up = self._active_line > 0
        can_move_down = self._active_line < len_options - 1

        if key == "HOME" and can_move_up:
            self._move_cursor(-self._active_line)
            self._active_line = 0

        elif key == "END" and can_move_down:
            self._move_cursor(len_options - self._active_line - 1)
            self._active_line = len_options - 1

        elif key == "UP" and can_move_up:
            self._active_line -= 1
            self._move_cursor(-1)

        elif key == "DOWN" and can_move_down:
            self._active_line += 1
            self._move_cursor(1)

        elif key == " " or key == "x":
            entry_value = self._options[self._active_line]["value"]
            if entry_value in self._active_options:
                self._active_options.remove(entry_value)
                self.write(f" \33[D")

            else:
                self._active_options.append(entry_value)
                self.write(f"x\33[D")

        elif key == "CTRL_M":
            self._move_cursor(len_options - self._active_line - 1)
            self.write(f"\r\n")
            return self._active_options

        return None

    def read_non_blocking(self):
        if not self._rendered:
            self._render()

        type, key = self.input_read_key()

        if type is None:
            return None

        return self._process_key(type, key)
