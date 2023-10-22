# SPDX-FileCopyrightText: Copyright (c) 2023 Petr Vavrin / pvavrin@gmail.com
#
# SPDX-License-Identifier: MIT


class Alias:
    _aliases = {}

    def alias_add(self, alias: str, command: str) -> None:
        self._aliases[alias] = command

    def alias_remove(self, alias: str) -> None:
        self._aliases.pop(alias, None)

    def alias_list(self) -> dict:
        return self._aliases

    def alias_get(self, alias: str) -> str:
        return self._aliases.get(alias, None)
