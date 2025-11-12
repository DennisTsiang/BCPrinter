#!/usr/bin/env python3

from nicegui import html, ui
import win32print
"""
ISBT 128 provides for unique identification of any donation event
worldwide. It does this by using a 13-character identifier built from three
elements, the first element identifies the facility that assigned the
number, the second the year, and the third a sequence number for the
donation. For example:
G1517 23 600001
Where:
G1517 identifies the Facility Identification Number (FIN) of the facility that
assigned the DIN (in this case Welsh Blood Service, Wales, United
Kingdom).
23 identifies the year in which the DIN was assigned.
600001 is the 6-digit sequence number controlled and maintained by the
facility assigning the DIN.
These first 13 characters comprise the Donation Identification Number
(DIN)
"""

zpl_code = {'value': ''}


def strip(text: str) -> str:
    if text is None or len(text) < 13:
        return ""
    stripped_string = text
    if stripped_string[0] == '=':
        stripped_string = stripped_string[1:]
    return stripped_string[:13]


def get_FIN(text: str) -> str:
    output = strip(text)
    return output[0:5]


def get_year(text: str) -> str:
    output = strip(text)
    return output[5:7]


def get_sequence_number(text: str) -> str:
    output = strip(text)
    return output[7:]


def generate_barcode_zpl(barcode: str) -> str:
    barcode = strip(barcode)
    zpl = "^XA\n" \
          "^BY2,2,80\n" \
          "^FO20,40^BC^{}^FS\n" \
          "^XZ".format(barcode)
    return zpl


def validate_input(text: str) -> bool:
    return text is not None and len(strip(text)) >= 13

def printer_button_enable(text: str) -> bool:
    return text is not None and len(strip(text)) == 13

def update_zpl(text: str) -> str:
    global zpl_code
    zpl = generate_barcode_zpl(text)
    zpl_code['value'] = zpl
    return zpl


# def open_print_dialog():
#     win32api.ShellExecute(0, "print", filename, '/d:"%s"' % win32print.GetDefaultPrinter(), ".", 0)
def get_printers():
    """Get list of available printers"""
    printers = [printer[2] for printer in win32print.EnumPrinters(2)]
    return printers


def send_zpl_to_printer(zpl_code, printer_name=None):
    """Send ZPL commands directly to a printer"""
    try:
        # Get default printer if none specified
        if printer_name is None:
            printer_name = win32print.GetDefaultPrinter()
        with open("zpl_output_test.txt", 'w') as f:
            f.write(zpl_code)
        ui.notification(f'Printed!')
    except Exception as e:
        ui.notify(f'Print error: {str(e)}', color='negative')


def root():
    user_input = ui.input(placeholder='Original Barcode')
    user_input.props('clearable')
    with html.section().style('font-size: 200%'):
        with ui.row():
            ui.label("Output Barcode:")
            with html.span().style("--nicegui-default-gap: 0; display: flex;").bind_visibility_from(
                    user_input, "value", validate_input):
                with html.span().style("color: red;"):
                    ui.label().bind_text_from(user_input, 'value', get_FIN)
                with html.span().style("color: blue;"):
                    ui.label().bind_text_from(user_input, 'value', get_year)
                with html.span().style("color: green"):
                    ui.label().bind_text_from(user_input, 'value', get_sequence_number)
            ui.label("Invalid barcode").style("color:red;").bind_visibility_from(
                user_input, "value", lambda x: x is not None and not len(x) == 0 and not validate_input(x))
    ui.label("ZPL Preview:").style('font-size: 120%')
    with ui.card().props('flat bordered'):
        ui.label().style('white-space: pre-wrap').bind_text_from(user_input, 'value', update_zpl)
    printer_select = ui.select(get_printers(),
                               label='Select Printer',
                               value=win32print.GetDefaultPrinter())
    ui.button(icon="print",
              on_click=lambda: send_zpl_to_printer(zpl_code['value'], printer_select.value)) \
    .props("size=xl") \
    .tooltip("Print") \
    .bind_enabled_from(user_input, 'value', printer_button_enable)


# Main

ui.run(root=root,
       title="Royal Papworth Hospital Barcode Printing Ver (2.00)",
       window_size=(500, 550),
       favicon="🖨️",
       reload=False)
