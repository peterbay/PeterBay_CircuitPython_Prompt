import usb_cdc

from peterbay_prompt.single_select import SingleSelect

serial = usb_cdc.console

select = SingleSelect(serial)
select.set_label("Select one option:")
select.set_options(
    [
        {"label": "Option 1", "value": "option1"},
        {"label": "Option 2", "value": "option2"},
        {"label": "Option 3", "value": "option3"},
        {"label": "Option 4", "value": "option4"},
    ]
)
select.set_active_option("option3")

while True:
    try:
        result = select.read_non_blocking()
        if result is not None:
            print("Result: ", result)
            break

    except KeyboardInterrupt:
        select.keyboard_interrupt()
        continue
