def strip(text: str, output_mode_selection: int) -> str:
    if text is None or (output_mode_selection <= 2 and len(text) < 13):
        return ""
    if output_mode_selection == 3:
        return text
    stripped_string = text
    if stripped_string[0] == '=':
        stripped_string = stripped_string[1:]
    if output_mode_selection == 1:
        return stripped_string[:13]
    elif output_mode_selection == 2:
        return stripped_string[:15]
    else:
        return text

def validate_input(text: str, mode: int = 0) -> bool:
    if text is None:
        return False
    if mode == 1:
        return len(strip(text, mode)) >= 13
    elif mode == 2:
        return len(strip(text, mode)) >= 15 and text[-2:].isdigit() and int(text[-2:]) >= 20
    elif mode == 3:
        return True

class OutputBarcode:
    def __init__(self, user_input: str, output_mode_selection: int, show_on_valid_input: bool = True):
        self.user_input = user_input
        self.output_mode_selection = output_mode_selection
        self.show_on_valid_input = show_on_valid_input
        self.visible: bool = False

    def set_visibility(self) -> None:
        self.visible = self.output_mode_selection <= 2 and self.user_input is not None and len(self.user_input) > 0
        if self.show_on_valid_input:
            self.visible = self.visible and validate_input(self.user_input, self.output_mode_selection)
        else:
            self.visible = self.visible and not validate_input(self.user_input, self.output_mode_selection)
    
    def update(self, user_input: str, output_mode_selection: int):
        self.user_input = user_input
        self.output_mode_selection = output_mode_selection
        self.set_visibility()