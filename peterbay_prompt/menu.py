# SPDX-FileCopyrightText: Copyright (c) 2023 Petr Vavrin / pvavrin@gmail.com
#
# SPDX-License-Identifier: MIT

import gc
from .prompt import Prompt
from .serial_io import SerialIO


class Menu(SerialIO):
    _enable_exit = False
    _menu_config = {}
    _actual_menu = {}
    _actual_path = []
    _menu_delimiter = "+" + "-" * 50 + "+"

    def __init__(self, serial: object) -> None:
        super().__init__(serial)
        self.prompt = Prompt(serial)

    def set_config(self, menu_config: dict = None) -> None:
        self._menu_config = menu_config
        self._actual_menu = menu_config
        self._actual_path = []

    def enable_exit(self, value: bool) -> None:
        self._enable_exit = value

    def _path_to_list(self, path: str) -> list[str]:
        path_list = path
        if isinstance(path_list, str):
            path_list = path_list.split(".")

        assert isinstance(
            path_list, list
        ), "Path must be list or string with dot separator"

        return path_list[:]

    def _get_item_by_path(self, menu, path):
        path_list = self._path_to_list(path)

        if len(path_list) == 0:
            raise ValueError("[_get_item_by_path] Path is empty")

        path_part = path_list.pop(0)

        if path_part == menu["id"]:
            if len(path_list) == 0:
                return menu

            path_part = path_list.pop(0)

        child = self._get_child_by(menu, "id", path_part)

        if child:
            return self._get_item_by_path(child, path_list) if len(path_list) else child

        return None

    def init_path(self, path: str) -> None:
        menu = self._get_item_by_path(self._menu_config, path)
        if not menu:
            raise ValueError("[init_path] Menu not found")

        self._actual_menu = menu
        self._actual_path = self._path_to_list(path)

    def _print_menu_line(self, line: str) -> None:
        self.write_line(f"|{line: <50}|")

    def _get_child_by(self, menu, key, value):
        if "childs" in menu:
            for child in menu["childs"]:
                if key in child:
                    if child[key] == value:
                        return child
        return None

    def _get_value(self, menu_item: dict, format_string: str = None) -> str:
        if "get_value" in menu_item:
            if callable(menu_item["get_value"]):
                value = menu_item["get_value"](self, self._actual_path, menu_item)
                return format_string.format(str(value)) if format_string else str(value)
        return ""

    def action_hotkey(self, hotkey: str) -> None:
        menu_item = self._get_child_by(self._actual_menu, "hotkey", hotkey)
        if menu_item:
            if "action" in menu_item:
                if callable(menu_item["action"]):
                    menu_item["action"](self, self._actual_path, menu_item)

            if "childs" in menu_item:
                self._actual_menu = menu_item
                self._actual_path.append(menu_item["id"])
            self.render()

    def action_back(self) -> bool:
        if len(self._actual_path) > 1:
            self._actual_path.pop()
            self._actual_menu = self._get_item_by_path(
                self._menu_config, self._actual_path
            )
            self.render()
            return False

        return True

    def action_reset(self) -> None:
        self._actual_menu = self._menu_config
        self._actual_path = [self._actual_menu["id"]]

    def _get_path_labels(self, path):
        path_list = self._path_to_list(path)
        labels = []
        menu = self._menu_config
        for path_part in path_list:
            menu = self._get_item_by_path(menu, path_part)
            if not menu:
                break

            labels.append(menu["label"])

        return labels

    def get_prompt_label(self, prompt: str) -> str:
        menu_labels = self._get_path_labels(self._actual_path)
        return " / ".join(menu_labels) + " " + prompt

    def render(self) -> None:
        menu_labels = self._get_path_labels(self._actual_path)
        label = " / ".join(menu_labels)
        parent_value = self._get_value(self._actual_menu, ", value: {0}")

        self.write_line(self._menu_delimiter)
        self._print_menu_line(f" {label}{parent_value}")
        self.write_line(self._menu_delimiter)

        child_index = 1
        if "childs" in self._actual_menu:
            for child in self._actual_menu["childs"]:
                if not "hotkey" in child:
                    child["hotkey"] = str(child_index)

                hotkey = child.get("hotkey", "")
                value = self._get_value(child, " val: {0}")
                has_childs = " >> " if "childs" in child else ""
                label = child.get("label", "")

                self._print_menu_line(
                    f" {hotkey: >2}. {label: <20} {has_childs}{value}"
                )
                child_index += 1

        back_label = None
        if len(self._actual_path) > 1:
            back_label = "Back"

        elif self._enable_exit:
            back_label = "Exit"

        if back_label:
            self._print_menu_line(" {0: >2}. {1}".format(0, back_label))

        self.write_line(self._menu_delimiter)
        gc.collect()

    def keyboard_interrupt(self) -> None:
        self.prompt.keyboard_interrupt()

    def read_non_blocking(self, prompt_string: str = "> ") -> list:
        entry = self.prompt.read_non_blocking(prompt_string)
        if entry is None:
            return None

        user_input = entry.strip()
        if user_input == "0":
            top_level = self.action_back()

            if top_level and self._enable_exit:
                self.write("\r\n")
                return True

        elif user_input == "reset":
            self.action_reset()
            self.render()

        elif user_input == "menu":
            self.render()

        else:
            self.action_hotkey(user_input)

        return None
