import usb_cdc

from peterbay_prompt.multi_select import MultiSelect

serial = usb_cdc.console

select = MultiSelect(serial)
select.set_label("Select one or more options:")
select.set_options(
    [
        {"label": "Option 1", "value": "option1"},
        {"label": "Option 2", "value": "option2"},
        {"label": "Option 3", "value": "option3"},
        {"label": "Option 4", "value": "option4"},
    ]
)
select.set_active_options(["option3"])

while True:
    try:
        result = select.read_non_blocking()
        if result is not None:
            print("Result: ", result)
            break

    except KeyboardInterrupt:
        select.keyboard_interrupt()
        continue

