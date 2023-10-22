# SPDX-FileCopyrightText: Copyright (c) 2023 Petr Vavrin / pvavrin@gmail.com
#
# SPDX-License-Identifier: MIT


class Cursor:
    CURSOS_DEFAULT = 0
    CURSOS_BLOCK_BLINKING = 1
    CURSOS_BLOCK_STEADY = 2
    CURSOS_UNDERLINE_BLINKING = 3
    CURSOS_UNDERLINE_STEADY = 4
    CURSOS_VERTICAL_LINE_BLINKING = 5
    CURSOS_VERTICAL_LINE_STEADY = 6

    def cursor_type(self, type: int) -> str:
        assert 0 <= type <= 6, "Cursor type must be between 0 and 6"

        return f"\33[{type} q"
