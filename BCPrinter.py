#!/usr/bin/env python3

from nicegui import html, ui
import win32print
import requests
import base64
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
zpl_preview_image_data: dict[str, str] = {'source': ''}
ui_images: dict[str, ui.image | None] = {'zpl_preview': None}

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
    zpl = "^XA" \
          "^BY3,2,100" \
          "^FO25,40^BC^FD{}^FS" \
          "^XZ".format(barcode)
    return zpl


def validate_input(text: str) -> bool:
    return text is not None and len(strip(text)) >= 13


def update_zpl(text: str):
    global zpl_code, ui_images
    zpl = generate_barcode_zpl(text)
    zpl_code['value'] = zpl
    if ui_images['zpl_preview'] is not None and validate_input(text):
        labelary_zpl_preview_image()


def labelary_zpl_preview_image():
    global zpl_code, zpl_preview_image_data, ui_images
    # adjust print density (12dpmm), label width (2 inches), label height (1 inches), and label index (0) as necessary
    if not zpl_code['value'] is None and len(zpl_code['value']) > 0:
        url = 'http://api.labelary.com/v1/printers/12dpmm/labels/2x1/0/'
        response = requests.post(url, data = zpl_code['value'], stream = True)
        if response.status_code == 200:
            base64_image = base64.b64encode(response.content).decode('utf-8')
            zpl_preview_image_data['source'] = f'data:image/png;base64,{base64_image}'
            if ui_images['zpl_preview'] is not None:
                ui_images['zpl_preview'].update()
        elif response.status_code == 429:
            ui.notify('Error: Too many requests to Labelary API. Please wait and try again later.')
        else:
            ui.notify('Error: ' + response.text)


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
        ui.notify(f'Printed!')
    except Exception as e:
        ui.notify(f'Print error: {str(e)}', color='negative')


def root():
    global zpl_preview_image_data
    user_input = ui.input(placeholder='Original Barcode', on_change=lambda e: update_zpl(e.value))
    user_input.props('clearable')
    with html.section().style('font-size: 120%'):
        with ui.row():
            ui.label("Output Barcode:")
            with html.span().style("--nicegui-default-gap: 0; display: flex;").bind_visibility_from(
                    user_input, "value", validate_input):
                with html.span().classes('text-red-500 hover:bg-yellow-300'):
                    ui.label().bind_text_from(user_input, 'value', get_FIN).tooltip("Facility Identification Number (FIN)")
                with html.span().classes('text-blue-500 hover:bg-yellow-300'):
                    ui.label().bind_text_from(user_input, 'value', get_year).tooltip("Year")
                with html.span().classes('text-green-500 hover:bg-yellow-300'):
                    ui.label().bind_text_from(user_input, 'value', get_sequence_number).tooltip("Sequence Number")
            ui.label("Invalid barcode").style("color:red;").bind_visibility_from(
                user_input, "value", lambda x: x is not None and not len(x) == 0 and not validate_input(x))
    ui.label("ZPL Preview:").style('font-size: 120%')
    zpl_preview = ui.image().style('width: 400px; height: 200px; border: 1px solid black;')
    ui_images['zpl_preview'] = zpl_preview
    zpl_preview.bind_source_from(zpl_preview_image_data)
    printer_select = ui.select(get_printers(),
                               label='Select Printer',
                               value=win32print.GetDefaultPrinter())
    ui.button(icon="print",
              on_click=lambda: send_zpl_to_printer(zpl_code['value'], printer_select.value)) \
    .props("size=xl") \
    .tooltip("Print") \
    .bind_enabled_from(user_input, 'value', validate_input)


# Main

ui.run(root=root,
       title="Royal Papworth Hospital Barcode Printing Ver (2.00)",
       window_size=(500, 605),
       favicon="🖨️",
       reload=False)
