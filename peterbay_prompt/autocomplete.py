# SPDX-FileCopyrightText: Copyright (c) 2023 Petr Vavrin / pvavrin@gmail.com
#
# SPDX-License-Identifier: MIT


class Autocomplete:
    _autocomplete_enabled = True
    _autocomplete_list = []
    _autocomplete_buffer = None
    _autocomplete_index = 0

    def autocomplete_set(self, autocomplete: list) -> None:
        if not self._autocomplete_enabled:
            return

        self._autocomplete_list = autocomplete

    def autocomplete_clean(self) -> None:
        self._autocomplete_index = 0
        self._autocomplete_buffer = None

    def autocomplete_process(self, entry: str) -> str:
        if not self._autocomplete_enabled or not self._autocomplete_list:
            return entry

        if self._autocomplete_buffer is None:
            self._autocomplete_buffer = entry

        matches = [
            match_entry
            for match_entry in self._autocomplete_list
            if match_entry.startswith(self._autocomplete_buffer)
        ]

        if matches:
            new_entry = matches[self._autocomplete_index % len(matches)]
            self._autocomplete_index += 1
            return new_entry

        return entry
