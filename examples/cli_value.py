import usb_cdc

from peterbay_prompt.value import Value

serial = usb_cdc.console

value = Value(serial)


def init_value_1(val: Value) -> None:
    val.reset()
    val.set_rules({"allowed_types": ["str"], "min_length": 3, "max_length": 10})
    val.write_line("\r\nEnter a string value between 3 and 10 characters long:")


def init_value_2(val: Value) -> None:
    val.reset()
    val.set_rules({"allowed_types": ["int"], "min": 0, "max": 1000})
    val.write_line("\r\nEnter a number between 0 and 1000:")


init_value_1(value)
value_number = 1

while True:
    try:
        result = value.read_non_blocking()
        if result is not None:
            print("Result: ", result)

            if value_number == 1:
                init_value_2(value)
                value_number = 2

            else:
                init_value_1(value)
                value_number = 1

    except KeyboardInterrupt:
        value.keyboard_interrupt()
        continue
