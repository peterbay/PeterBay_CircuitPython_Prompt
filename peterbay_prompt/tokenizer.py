# SPDX-FileCopyrightText: Copyright (c) 2023 Petr Vavrin / pvavrin@gmail.com
#
# SPDX-License-Identifier: MIT


class Tokenizer:
    def __init__(self):
        self._long_option_delimiters = ["="]

    def set_long_option_delimiters(self, delimiters: list):
        self._long_option_delimiters = delimiters

    def _read_until_chars(self, text: str, pos: int, chars: list) -> int:
        len_text = len(text)
        while pos < len_text and text[pos] not in chars:
            pos += 1

        return pos

    def _read_exclude_chars(self, text: str, pos: int, chars: list) -> int:
        len_text = len(text)
        while pos < len_text and text[pos] in chars:
            pos += 1

        return pos

    def _quoted_text(self, tokens: list, text: str, start: int, quote_char: str) -> int:
        pos = self._read_until_chars(text, start, [quote_char])
        tokens.append(
            {
                "type": "text",
                "content": text[start:pos],
                "quote": quote_char,
            }
        )
        return pos + 1

    def _long_option(self, tokens: list, text: str, start: int) -> int:
        pos = self._read_until_chars(text, start, self._long_option_delimiters + [" "])
        name = text[start:pos]
        delimiter = text[pos]

        token = {
            "type": "long_option",
            "name": name,
        }

        if delimiter not in self._long_option_delimiters:
            token["content"] = True
            tokens.append(token)
            return pos

        start = pos + 1

        if len(text) > start:
            quote = text[start]
            if quote in ['"', "'"]:
                pos = self._read_until_chars(text, start + 1, [quote])
                token["content"] = text[start + 1 : pos]
                token["quote"] = quote
                token["delimiter"] = delimiter
                tokens.append(token)
                return pos + 1

        pos = self._read_until_chars(text, start, [" "])
        token["content"] = text[start:pos]
        token["delimiter"] = delimiter
        tokens.append(token)
        return pos

    def _short_option(self, tokens: list, text: str, start: int) -> int:
        pos = self._read_until_chars(text, start, [" "])
        options = text[start:pos]
        for option in options:
            tokens.append(
                {
                    "type": "option",
                    "name": option,
                    "content": True,
                    "group": options,
                }
            )
        return pos

    def _text(
        self, tokens: list, text: str, start: int, support_key_value: bool = False
    ) -> int:
        delimiters = [" "]
        if support_key_value:
            delimiters.append("=")

        pos = self._read_until_chars(text, start, delimiters)
        content = text[start:pos]

        if support_key_value:
            if pos < len(text) and text[pos] == "=" and content.isalpha():
                tokens.append(
                    {
                        "type": "key_value",
                        "name": content,
                        "content": text[pos + 1 :],
                    }
                )
                return len(text)

        tokens.append(
            {
                "type": "text",
                "content": content,
            }
        )
        return pos

    def _space(self, tokens: list, text: str, start: int) -> int:
        pos = self._read_exclude_chars(text, start, [" "])
        tokens.append(
            {
                "type": "space",
                "content": " " + text[start:pos],
            }
        )
        return pos

    def to_dict(self, tokens: list) -> dict:
        command = None
        positional = []
        options = {}
        key_values = {}

        for token in tokens:
            content = token["content"]
            type = token["type"]

            if type == "text":
                if command is None:
                    command = content
                else:
                    positional.append(content)

            elif type in ["option", "long_option"] and "name" in token:
                options[token["name"]] = content

            elif type == "key_value":
                key_values[token["name"]] = content

        return {
            "command": command,
            "positional": positional,
            "options": options,
            "key_value": key_values,
        }

    def to_string(self, tokens: list) -> str:
        text = ""
        last_type = None
        for token in tokens:
            content = token["content"]

            if "quote" in token:
                content = token["quote"] + content + token["quote"]

            type = token.get("type", None)
            name = token.get("name", "")

            if type in ["space", "text"]:
                text += content

            elif type == "option":
                text += name if last_type == type else "-" + name

            elif type == "long_option":
                text += "--" + name

                if "delimiter" in token:
                    text += token["delimiter"]

                if not content == True:
                    text += content

            elif type == "key_value":
                text += name + "=" + content

            last_type = type

        return text

    def tokenize(self, text: str, options: dict = {}) -> list:
        limit = options["limit"] if "limit" in options else None
        key_value = bool(options["key_value"]) if "key_value" in options else False

        assert limit is None or limit > 0, "Limit must be positive"

        tokens = []
        i = 0
        count = 0
        while i < len(text):
            char = text[i]

            if char in ['"', "'"]:
                i = self._quoted_text(tokens, text, i + 1, char)

            elif char == "-":
                start = i + 1
                if start < len(text) and text[start] == "-":  # long option
                    i = self._long_option(tokens, text, start + 1)

                else:  # short option
                    i = self._short_option(tokens, text, start)

            elif char == " ":
                i = self._space(tokens, text, i + 1)

            else:
                i = self._text(tokens, text, i, key_value)

            count += 1

            if limit is None:
                continue

            if count >= limit:
                tokens.append(
                    {
                        "type": "text",
                        "content": text[i:],
                    }
                )
                break

        return tokens
