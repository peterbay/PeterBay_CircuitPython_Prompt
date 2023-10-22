# SPDX-FileCopyrightText: Copyright (c) 2023 Petr Vavrin / pvavrin@gmail.com
#
# SPDX-License-Identifier: MIT


class SerialIO:
    def __init__(self, serial: object) -> None:
        self._serial = serial
        self._serial_read = serial.read
        self._serial_write = serial.write
        self._serial.timeout = 0.03

    def write(self, text: str) -> None:
        self._serial_write(bytes(text, "ascii"))

    def write_line(self, text: str) -> None:
        self._serial_write(bytes(text + "\r\n", "ascii"))
