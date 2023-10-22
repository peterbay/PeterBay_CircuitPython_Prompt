# SPDX-FileCopyrightText: Copyright (c) 2023 Petr Vavrin / pvavrin@gmail.com
#
# SPDX-License-Identifier: MIT


class Colors:
    COLOR_BLACK = 0
    COLOR_RED = 1
    COLOR_GREEN = 2
    COLOR_YELLOW = 3
    COLOR_BLUE = 4
    COLOR_MAGENTA = 5
    COLOR_CYAN = 6
    COLOR_LIGHT_GRAY = 7
    COLOR_DARK_GRAY = 8
    COLOR_LIGHT_RED = 9
    COLOR_LIGHT_GREEN = 10
    COLOR_LIGHT_YELLOW = 11
    COLOR_LIGHT_BLUE = 12
    COLOR_LIGHT_MAGENTA = 13
    COLOR_LIGHT_CYAN = 14
    COLOR_WHITE = 15

    COLOR_LEVEL_NORMAL = None
    COLOR_LEVEL_ERROR = 1
    COLOR_LEVEL_WARNING = 3
    COLOR_LEVEL_INFO = 2
    COLOR_LEVEL_DEBUG = 5
    COLOR_LEVEL_TRACE = 8

    def colorize(self, text: str, bg_color: int, fg_color: int) -> str:
        assert (
            bg_color is None or self.COLOR_BLACK <= bg_color <= self.COLOR_WHITE
        ), f"BG color must be between {self.COLOR_BLACK} and {self.COLOR_WHITE}"

        assert (
            fg_color is None or self.COLOR_BLACK <= fg_color <= self.COLOR_WHITE
        ), f"FG color must be between {self.COLOR_BLACK} and {self.COLOR_WHITE}"

        decorators = []

        if bg_color is not None or fg_color is not None:
            decorators.append("\33[0m")

        if bg_color is not None:
            decorators.append(f"\33[48;5;{bg_color}m")

        if fg_color is not None:
            decorators.append(f"\33[38;5;{fg_color}m")

        if decorators:
            decorators.append(text)
            decorators.append("\33[0m")
            return "".join(decorators)

        return text

    def colorize_level(self, text: str, level: int) -> str:
        assert (
            level is None or self.COLOR_BLACK <= level <= self.COLOR_WHITE
        ), f"level must be between {self.COLOR_BLACK} and {self.COLOR_WHITE}"

        if level is None:
            return text

        return self.colorize(text, None, level)
