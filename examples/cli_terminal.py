import usb_cdc
from prompt.terminal import Terminal
from prompt.colors import Colors
from prompt.cursor import Cursor
from prompt.tokenizer import Tokenizer

serial = usb_cdc.console

colors = Colors()
cursor = Cursor()
tokenizer = Tokenizer()

terminal = Terminal(serial)
terminal.set_commands(
    [
        "set",
        "get",
        "settings",
        "reset",
        "restart",
        "password",
    ]
)

prompt_string = colors.colorize("$> ", None, colors.COLOR_GREEN)
prompt_string += cursor.cursor_type(cursor.CURSOS_VERTICAL_LINE_STEADY)


def process_command(tokens: list) -> None:
    tokens_dict = tokenizer.to_dict(tokens)

    command = tokens_dict.get("command", None)
    key_value = tokens_dict.get("key_value", None)
    positional = tokens_dict.get("positional", None)
    options = tokens_dict.get("options", None)

    terminal.write_line("Process command:")
    terminal.write_line(f"  command: {command}")
    terminal.write_line(f"  key_value: {key_value}")
    terminal.write_line(f"  positional: {positional}")
    terminal.write_line(f"  options: {options}")


while True:
    try:
        cmd = terminal.read_non_blocking(prompt_string)

        if cmd:
            process_command(cmd)

    except KeyboardInterrupt:
        terminal.keyboard_interrupt()
        continue
