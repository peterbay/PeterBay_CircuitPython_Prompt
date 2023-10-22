# SPDX-FileCopyrightText: Copyright (c) 2023 Petr Vavrin / pvavrin@gmail.com
#
# SPDX-License-Identifier: MIT

from .serial_io import SerialIO
from .prompt import Prompt
from .tokenizer import Tokenizer
from .alias import Alias


class Terminal(SerialIO):
    _commands = {}
    _help_message = ""
    _internal_commands = ["alias", "clear", "unalias", "help", "history"]

    def __init__(self, serial: object) -> None:
        super().__init__(serial)
        self.prompt = Prompt(serial)
        self.tokenizer = Tokenizer()
        self.alias = Alias()

    def set_commands(self, commands: list) -> None:
        self._commands = commands

    def _get_commands_list(self) -> list:
        commands = self._internal_commands + self._commands
        commands.sort()
        return commands

    def _process_internal_commands(self, tokens: list) -> bool:
        tokens_dict = self.tokenizer.to_dict(tokens)

        command = tokens_dict.get("command", None)
        key_value = tokens_dict.get("key_value", None)
        positional = tokens_dict.get("positional", None)
        options = tokens_dict.get("options", None)

        if command == "alias":
            if not key_value and not positional and not options:
                self.write_line("Aliases:")
                for alias, command in self.alias.alias_list().items():
                    self.write_line(f"  {alias} = {command}")

            elif key_value and not positional and not options:
                alias_name = list(key_value)[0]
                self.alias.alias_add(alias_name, key_value[alias_name])

            else:
                self.write_line("Invalid alias arguments")

            return True

        elif command == "unalias":
            if positional:
                self.alias.alias_remove(positional[0])

            else:
                self.write_line("Invalid unalias arguments")

            return True

        elif command == "help":
            commands = self._get_commands_list()
            if self._help_message:
                self.write_line(self._help_message)
            self.write_line("Commands: ")
            comands_list = ", ".join(commands)
            self.write_line(f"  {comands_list}")
            return True

        elif command == "free":
            import gc

            gc.collect()
            allocated = gc.mem_alloc()
            free = gc.mem_free()
            self.write_line(f" Allocated memory : {allocated}")
            self.write_line(f" Free memory      : {free}")
            return True

        return False

    def _parse_buffer(self, buffer: str, level: int = 0) -> list:
        tokens = self.tokenizer.tokenize(buffer.lstrip(), {"key_value": True})

        command = None
        if len(tokens) > 0:
            if tokens[0]["type"] == "text":
                command = tokens[0]["content"]

        if command and level < 5:
            command_rest = self.tokenizer.to_string(tokens[1:])
            aliases = self.alias.alias_list()
            if command in aliases:
                return self._parse_buffer(
                    aliases[command] + " " + command_rest, level + 1
                )

        return tokens

    def keyboard_interrupt(self) -> None:
        self.prompt.keyboard_interrupt()

    def read_non_blocking(self, prompt_string: str = "> ") -> list:
        self.prompt.autocomplete_set(self._get_commands_list())

        entry = self.prompt.read_non_blocking(prompt_string)
        if entry is None:
            return None

        tokens = self._parse_buffer(entry)
        processed = self._process_internal_commands(tokens)
        if processed:
            return None

        return tokens
