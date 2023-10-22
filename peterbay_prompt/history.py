# SPDX-FileCopyrightText: Copyright (c) 2023 Petr Vavrin / pvavrin@gmail.com
#
# SPDX-License-Identifier: MIT


class History:
    HISTORY_PREV = 1
    HISTORY_NEXT = 2
    _history_size = 30
    _history = []
    _history_index = -1
    _history_enabled = True
    _history_actual_entry = ""

    def history_get(self) -> list:
        return self._history

    def history_set(self, history: list) -> None:
        if self._history_size:
            self._history = history
            self._history_index = len(history)

    def history_clean(self):
        self._history = []
        self._history_index = -1

    def history_set_size(self, size: int):
        assert size >= 0, "History size must be positive"
        if size != self._history_size:
            self._history = self._history[-size:]

        self._history_size = size

    def history_action(self, action: int, entry: str) -> str:
        len_history = len(self._history)

        if not self._history_enabled or len_history == 0:
            return entry

        idx = self._history_index

        if idx == len_history:
            self._history_actual_entry = entry

        if action == self.HISTORY_PREV and idx > 0:
            idx -= 1
            entry = self._history[idx]

        elif action == self.HISTORY_NEXT:
            size = len_history - 1

            if self._history and idx < size:
                idx += 1
                entry = self._history[idx]

            elif idx == size:
                idx += 1
                entry = self._history_actual_entry

        self._history_index = idx

        return entry

    def history_append(self, entry: str) -> None:
        if len(entry.strip()) == 0:
            return None

        if not self._history_enabled or self._history_size == 0:
            return None

        len_history = len(self._history)

        if not len_history or (len_history and not self._history[-1] == entry):
            self._history.append(entry)

            if len_history + 1 > self._history_size:
                self._history.pop(0)

        self._history_index = len(self._history)

    def history_get_entry(self, command: str) -> str:
        if len(command) < 2 or len(self._history) == 0:
            return None

        if not command[0] == "!":
            return None

        if command == "!!":
            command = "!-1"

        if command[1].isdigit() or command[1] == "-":
            try:
                return self._history[int(command[1:])]
            except:
                return None

        else:
            for entry in reversed(self._history):
                if entry.startswith(command[1:]):
                    return entry
