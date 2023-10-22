# SPDX-FileCopyrightText: Copyright (c) 2023 Petr Vavrin / pvavrin@gmail.com
#
# SPDX-License-Identifier: MIT

from .input import Input
from .autocomplete import Autocomplete
from .history import History


class Prompt(Input, Autocomplete, History):
    _last_key = None
    _copy_text = ""
    _last_key = None

    _autocomplete_enabled = True
    _history_enabled = True
    _new_prompt_string = True
    _commands_enabled = True
    _clear_screen_enabled = True

    def __init__(self, serial: object):
        super().__init__(serial)
        self._clear()
        self.set_max_length(120)

    def _clear(self) -> None:
        self._buffer = ""
        self._cursor = 0

    def set_max_length(self, length: int) -> None:
        assert length >= 0, "Max length must be positive"
        self._max_length = length

    def enable_commands(self, value: bool) -> None:
        self._commands_enabled = value

    def enable_clear_screen(self, value: bool) -> None:
        self._clear_screen_enabled = value

    def set_buffer(self, buffer: str) -> None:
        self._buffer = buffer
        self._cursor = len(buffer)

    def _clear_screen(self, clear_buffer=False) -> None:
        self.write(f"\33[2J\33[1;1H")

        if clear_buffer:
            self._clear()
            return

        self.write(self._prompt_string + self._buffer)
        pos = len(self._buffer) - self._cursor
        self.write(f"\33[{pos}D")

    def _replace_buffer(self, new_buffer):
        if new_buffer == self._buffer:
            return

        self._move_cursor(-self._cursor)
        self._clear()
        self.write(f"\33[K")
        self._add_chars(new_buffer)

    def _move_cursor(self, count):
        if count < 0:
            count = max(count, -self._cursor)
            abs_count = abs(count)
            if abs_count:
                self.write(f"\33[{abs_count}D")

        elif count > 0:
            count = min(count, len(self._buffer) - self._cursor)
            if count:
                self.write(f"\33[{count}C")

        self._cursor += count
        return count

    def _set_copy_text(self, key, count, text):
        if self._last_key == key or self._last_key == None:
            if count < 0:
                self._copy_text = text + self._copy_text

            elif count > 0:
                self._copy_text = self._copy_text + text
        else:
            self._copy_text = text

    def _remove_chars(self, count, copy_on_key=None):
        buffer = self._buffer
        if count < 0:
            if self._cursor == 0:
                return

            count = abs(self._move_cursor(count))

        elif count > 0:
            count = min(count, len(buffer) - self._cursor)

        if copy_on_key:
            self._set_copy_text(
                copy_on_key, count, buffer[self._cursor : self._cursor + count]
            )

        self._buffer = buffer[: self._cursor] + buffer[self._cursor + count :]

        self.write(f"\33[{count}P")

    def _add_chars(self, chars):
        if len(self._buffer) + len(chars) > self._max_length:
            return

        if self._cursor == len(self._buffer):
            self._buffer += chars
            self._cursor += len(chars)
            self.write(chars)
            return

        rest = self._buffer[self._cursor :]
        self._buffer = self._buffer[: self._cursor] + chars + rest
        self._cursor += len(chars) + len(rest)
        self.write(f"{chars}{rest}")
        self._move_cursor(-len(rest))

    def _get_word_start(self):
        buffer = self._buffer
        i = self._cursor - 1

        while i >= 0 and buffer[i] in [" "]:
            i -= 1

        while i >= 0 and buffer[i] not in [" "]:
            i -= 1

        return i - self._cursor + 1

    def _get_word_end(self):
        buffer = self._buffer
        i = self._cursor
        len_buffer = len(buffer)

        while i < len_buffer and buffer[i] in [" "]:
            i += 1

        while i < len_buffer and buffer[i] not in [" "]:
            i += 1

        return i - self._cursor

    def _internal_commands(self) -> tuple:
        buffer = self._buffer.strip()
        buffer_len = len(buffer)

        if self._history_enabled and buffer_len > 0:
            if buffer == "clear":
                self._clear_screen(True)

                return True, None

            if buffer == "history":
                history = self.history_get()
                for i, entry in enumerate(history):
                    self.write(f"{i:>3}: {entry}\r\n")

                return True, None

            elif buffer[0] == "!":
                entry = self.history_get_entry(buffer)
                if entry:
                    self.write(f"{entry}\r\n")
                    self._clear()

                    return False, entry

        return False, buffer

    def _process_key(self, type: int, key: str) -> bool:
        if not key == "CTRL_I" and self._autocomplete_enabled:  # NOT a Tab key
            self.autocomplete_clean()

        if type == self.INPUT_CHAR:
            self._add_chars(key)
            return True

        if key == "LEFT" or key == "CTRL_B":
            self._move_cursor(-1)

        elif key == "RIGHT" or key == "CTRL_F":
            self._move_cursor(1)

        elif key == "HOME" or key == "CTRL_A":
            self._move_cursor(-self._cursor)

        elif key == "END" or key == "CTRL_E":
            self._move_cursor(len(self._buffer) - self._cursor)

        elif key == "BACKSPACE" or key == "CTRL_H":
            self._remove_chars(-1)

        elif key == "DELETE":
            self._remove_chars(1)

        elif key == "CTRL_I" and self._autocomplete_enabled and self._commands_enabled:
            self._replace_buffer(self.autocomplete_process(self._buffer))

        elif key == "CTRL_K":
            self._remove_chars(len(self._buffer) - self._cursor, key)

        elif key == "CTRL_U":
            self._remove_chars(-self._cursor, key)

        elif key == "ALT_B":
            self._move_cursor(self._get_word_start())

        elif key == "CTRL_W":
            self._remove_chars(self._get_word_start(), key)

        elif key == "ALT_D":
            self._remove_chars(self._get_word_end(), key)

        elif key == "ALT_F":
            self._move_cursor(self._get_word_end())

        elif key == "CTRL_L" and self._clear_screen_enabled:
            self._clear_screen()

        elif key == "CTRL_Y" and self._copy_text:
            self._add_chars(self._copy_text)

        elif (
            (key == "UP" or key == "CTRL_P")
            and self._history_enabled
            and self._commands_enabled
        ):
            self._replace_buffer(self.history_action(self.HISTORY_PREV, self._buffer))

        elif (
            (key == "DOWN" or key == "CTRL_N")
            and self._history_enabled
            and self._commands_enabled
        ):
            self._replace_buffer(self.history_action(self.HISTORY_NEXT, self._buffer))

        else:
            return False

        self._last_key = key

        return True

    def keyboard_interrupt(self) -> None:
        self.write("\r\n")
        self._clear()
        self._new_prompt_string = True

    def read_non_blocking(self, prompt_string: str = "> ") -> str:
        if self._new_prompt_string:
            self._new_prompt_string = False
            self._prompt_string = prompt_string
            self.write(prompt_string)
            if self._buffer:
                self.write(self._buffer)
            else:
                self._clear()

        type, key = self.input_read_key()

        if type is None:
            return None

        # print(type, key)

        key_processed = self._process_key(type, key)
        if key_processed:
            return None

        if key == "CTRL_M":
            self.write("\r\n")

            if self._commands_enabled:
                is_internal, buffer = self._internal_commands()
                if is_internal:
                    self.write(prompt_string)
                    self._clear()
                    return None

            if self._history_enabled:
                self.history_append(buffer)

            self._new_prompt_string = True
            self._clear()
            return buffer
