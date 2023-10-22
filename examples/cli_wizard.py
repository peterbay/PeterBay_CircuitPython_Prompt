import usb_cdc
import peterbay_prompt.wizard as wizard

serial = usb_cdc.console

wizard = wizard.Wizard(serial)

wizard_questions = [
    {
        "name": "questio_1",
        "type": "select",
        "question": "Select one option:",
        "data": [
            {"label": "Option 1", "value": "option1"},
            {"label": "Option 2", "value": "option2"},
            {"label": "Option 3", "value": "option3"},
            {"label": "Option 4", "value": "option4"},
        ],
    },
    {
        "name": "question_2",
        "type": "value",
        "default": "123",
        "question": "Enter value [number]:",
        "rules": {"allowed_types": ["int", "float"]},
    },
    {
        "name": "question_3",
        "type": "value",
        "default": False,
        "question": "Enter value [yes/no]:",
        "rules": {"allowed_types": ["bool"]},
        "settings": {"boolean": {"true": "yes", "false": "no"}},
    },
]

wizard_header = (
    "\r\nHere is example of a wizard.\r\nYou can use it to configure your device.\r\n"
)

wizard.set_config(wizard_header, wizard_questions)

while True:
    try:
        result = wizard.read_non_blocking()
        if result is not None:
            print("Result: ", result)
            break

    except KeyboardInterrupt:
        wizard.keyboard_interrupt()

while True:
    pass
