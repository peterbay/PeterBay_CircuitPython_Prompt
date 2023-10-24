import gc
import usb_cdc

from peterbay_prompt.menu import Menu

serial = usb_cdc.console


menu = Menu(serial)
menu.enable_exit(True)


class App:
    def __init__(self):
        self._brightness = 50
        self._contrast = 50

    def get_value(self, menu_object: object, path: list, item: object) -> None:
        if item["id"] == "brightness":
            return self._brightness

        elif item["id"] == "contrast":
            return self._contrast

        return ""

    def on_action(self, menu_object: object, path: list, item: object) -> None:
        if path[-1] == "brightness":
            if item["id"] == "increase":
                self._brightness += 1

            elif item["id"] == "decrease":
                self._brightness -= 1

        elif path[-1] == "contrast":
            if item["id"] == "increase":
                self._contrast += 1

            elif item["id"] == "decrease":
                self._contrast -= 1

        elif item["id"] == "memory":
            gc.collect()
            allocated = gc.mem_alloc()
            free = gc.mem_free()
            menu_object.write_line(f" Allocated memory : {allocated}")
            menu_object.write_line(f" Free memory      : {free}")

app = App()

menu_config = {
    "id": "main",
    "label": "Main",
    "childs": [
        {
            "id": "memory",
            "label": "Memory",
            "action": app.on_action,
        },
        {
            "id": "brightness",
            "label": "Brightness",
            "get_value": app.get_value,
            "childs": [
                {
                    "id": "increase",
                    "label": "Increase",
                    "action": app.on_action,
                },
                {
                    "id": "decrease",
                    "label": "Decrease",
                    "action": app.on_action,
                },
            ],
        },
        {
            "id": "contrast",
            "label": "Contrast",
            "get_value": app.get_value,
            "childs": [
                {
                    "id": "increase",
                    "label": "Increase",
                    "action": app.on_action,
                },
                {
                    "id": "decrease",
                    "label": "Decrease",
                    "action": app.on_action,
                },
            ],
        },
    ],
}


menu.set_config(menu_config)
menu.init_path("main")
menu.render()

prompt_string = "#> "

while True:
    try:
        result = menu.read_non_blocking(prompt_string)
        if result == True:
            break

    except KeyboardInterrupt:
        menu.keyboard_interrupt()
        continue
