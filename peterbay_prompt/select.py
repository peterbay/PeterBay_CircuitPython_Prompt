# SPDX-FileCopyrightText: Copyright (c) 2023 Petr Vavrin / pvavrin@gmail.com
#
# SPDX-License-Identifier: MIT

from .input import Input


class Select(Input):
    _rendered = False
    _options = []
    _active_option = None
    _active_option_index = None
    _active_line = None
    _question = None

    def set_question(self, question: str) -> None:
        self._question = question
        self._rendered = False

    def set_options(self, options: list) -> None:
        self._options = options
        self._rendered = False

    def set_active_option(self, option: str) -> None:
        self._active_option = option
        self._active_option_index = None
        self._active_line = None
        self._rendered = False

    def _write_option_line(self, index: int, entry: dict, render_label: bool) -> None:
        mark = " "

        if self._active_option is None:
            self._active_option = entry["value"]

        if entry["value"] == self._active_option:
            mark = "x"

            if self._active_line is None:
                self._active_line = index

            if self._active_option_index is None:
                self._active_option_index = index

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
        if self._question:
            self.write_line(self._question)

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
            cursor_diff = self._active_option_index - self._active_line
            if cursor_diff == 0:
                return None

            self.write(f"\33[sx\33[D")
            self._move_cursor(cursor_diff)
            self.write(f" \33[D\33[u")

            self._active_option = self._options[self._active_line]["value"]
            self._active_option_index = self._active_line

        elif key == "CTRL_M":
            self._move_cursor(len_options - self._active_line - 1)
            self.write(f"\r\n")
            return self._active_option

        return None

    def read_non_blocking(self):
        if not self._rendered:
            self._render()

        type, key = self.input_read_key()

        if type is None:
            return None

        return self._process_key(type, key)
