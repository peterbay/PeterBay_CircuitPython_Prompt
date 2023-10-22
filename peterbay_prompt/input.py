# SPDX-FileCopyrightText: Copyright (c) 2023 Petr Vavrin / pvavrin@gmail.com
#
# SPDX-License-Identifier: MIT

from .serial_io import SerialIO


class Input(SerialIO):
    INPUT_CHAR = 1
    INPUT_CTRL_CODE = 2
    INPUT_ESCAPE_CODE = 3
    INPUT_DATA = 4

    _input_slecial_keys = {
        "A": "UP",
        "B": "DOWN",
        "C": "RIGHT",
        "D": "LEFT",
        "F": "END",
        "H": "HOME",
        "P": "F1",
        "Q": "F2",
        "R": "F3",
        "S": "F4",
    }

    _input_parameter_codes = {
        "1": "HOME",
        "2": "INSERT",
        "3": "DELETE",
        "4": "END",
        "5": "PGUP",
        "6": "PGDW",
        "7": "HOME",
        "8": "END",
        "15": "F5",
        "17": "F6",
        "18": "F7",
        "19": "F8",
        "20": "F9",
        "21": "F10",
        "23": "F11",
        "24": "F12",
    }

    _input_escape_modifiers = {
        "~": "",
        "2": "SHIFT",
        "3": "ALT",
        "4": "ALT_SHIFT",
        "5": "CONTROL",
        "6": "CONTROL_SHIFT",
        "7": "CONTROL_ALT",
        "8": "CONTROL_ALT_SHIFT",
    }

    def _input_read_in_range(
        self,
        from_char_ord: int,
        to_char_ord: int,
        char: str = None,
        read_next: bool = True,
    ):
        read = self._serial_read
        buffer = ""
        if char is None:
            char = read(1).decode("ascii")

        char_ord = ord(char)

        while from_char_ord <= char_ord <= to_char_ord:
            buffer += char
            if read_next:
                char = read(1).decode("ascii")
                char_ord = ord(char)

            else:
                char = None
                break

        return buffer, char

    def _input_decode_escape_code(
        self, parameter: str, intermediate: str, final: str
    ) -> str:
        modifier = None
        modifier_code = ""
        key_code = self._input_slecial_keys.get(final, None) if final != "~" else None

        if not parameter and not intermediate:
            return key_code

        if ";" in parameter:
            parameter, modifier = parameter.split(";")
            modifier_code = self._input_escape_modifiers.get(modifier, None)

        if parameter == "1" and modifier_code and key_code:
            return f"{modifier_code}_{key_code}"

        elif parameter and not intermediate and final == "~":
            parameter_code = self._input_parameter_codes.get(parameter, None)
            if parameter_code:
                if modifier_code:
                    return f"{modifier_code}_{parameter_code}"
                else:
                    return parameter_code

        return None

    def _input_read_escape_code(self) -> str:
        read = self._serial_read
        code = read(1).decode("ascii")
        ord_code = ord(code)

        if ord_code == 91:  # char [
            # For Control Sequence Introducer, or CSI, commands, the ESC [
            # (written as \e[ or \033[ in several programming and scripting languages)
            # is followed by any number (including none) of "parameter bytes" in the range 0x30–0x3F (ASCII 0–9:;<=>?),
            # then by any number of "intermediate bytes" in the range 0x20–0x2F (ASCII space and !"#$%&'()*+,-./),
            # then finally by a single "final byte" in the range 0x40–0x7E (ASCII @A–Z[\]^_`a–z{|}~).[5]: 5.4

            char = read(1).decode("ascii")
            parameter, char = self._input_read_in_range(0x30, 0x3F, char)
            intermediate, char = self._input_read_in_range(0x20, 0x2F, char)
            final, char = self._input_read_in_range(0x40, 0x7E, char, False)

            decoded_escape = self._input_decode_escape_code(
                parameter, intermediate, final
            )
            if decoded_escape:
                return decoded_escape

            return f"{code}{parameter}{intermediate}{final}"

        elif 0 < ord_code < 32:
            char = chr(ord_code + 64)
            return f"CTRL_ALT_{char}"

        elif ord_code == 79:
            ext_code = read(1).decode("ascii")
            return self._input_slecial_keys.get(ext_code, f"{code}{ext_code}")

        elif 96 < ord_code < 123:
            char = chr(ord_code - 32)
            return f"ALT_{char}"

        return code

    def input_read_key(self) -> (int, str):
        if self._serial.in_waiting:
            try:
                char = self._serial_read(1).decode("ascii")

                ord_char = ord(char)

                if ord_char == 27:
                    if not self._serial.in_waiting:
                        return self.INPUT_ESCAPE_CODE, "ESC"

                    try:
                        return self.INPUT_ESCAPE_CODE, self._input_read_escape_code()

                    except UnicodeError:
                        return None, None

                elif 0 <= ord_char < 32:
                    char = chr(ord_char + 64)
                    return self.INPUT_CTRL_CODE, f"CTRL_{char}"

                elif 32 <= ord_char < 127:
                    return self.INPUT_CHAR, char

                elif ord_char == 127:
                    return self.INPUT_CTRL_CODE, "BACKSPACE"

            except KeyboardInterrupt:
                return self.INPUT_CTRL_CODE, "CTRL_C"

            except UnicodeError:
                return None, None

        return None, None
