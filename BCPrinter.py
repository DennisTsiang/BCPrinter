#!/usr/bin/env python3

from nicegui import html, ui
import win32print
import requests
import base64
import argparse
import threading
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

# Global Variables
zpl_code = {'value': ''}
zpl_preview_image_data: dict[str, str] = {'source': ''}
ui_images: dict[str, ui.image | None] = {'zpl_preview': None}
user_input: ui.input | None = None
printer_select: ui.select | None = None
debug_mode: bool = False
debounce_timer: threading.Timer | None = None
debounce_delay: float = 0.5  # seconds

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
    global zpl_code, ui_images, debounce_timer
    if debounce_timer is not None:
        debounce_timer.cancel()

    zpl = generate_barcode_zpl(text)
    zpl_code['value'] = zpl
    if ui_images['zpl_preview'] is not None and validate_input(text):
        debounce_timer = threading.Timer(debounce_delay, labelary_zpl_preview_image)
        debounce_timer.start()


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


def get_printers():
    """Get list of available printers"""
    printers = [printer[2] for printer in win32print.EnumPrinters(2)]
    return printers

def zebra_print_zpl(zpl_code: str, printer_name: str):
    """Send ZPL commands to Zebra printer using Win32 Print Spooler API"""
    try:
        # Open a handle to the printer
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            # Start a print job
            win32print.StartDocPrinter(hPrinter, 1, ("ZPL Print Job", None, "RAW"))
            try:
                # Start a page and write the ZPL code
                # These steps would typically be repeated for multiple pages
                win32print.StartPagePrinter(hPrinter)
                win32print.WritePrinter(hPrinter, zpl_code.encode('utf-8'))
                win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)
    except Exception as e:
        raise


def send_zpl_to_printer(zpl_code, debug=True, printer_name=None) -> bool:
    """Send ZPL commands directly to a printer"""
    try:
        # Get default printer if none specified
        if printer_name is None:
            printer_name = win32print.GetDefaultPrinter()
        if debug:
            filename = f"{printer_name}.txt"
            with open(filename, 'w') as f:
                f.write(zpl_code)
        else:
            zebra_print_zpl(zpl_code, printer_name)
        ui.notify(f'Printed!')
        return True
    except Exception as e:
        ui.notify(f'Print error: {str(e)}', color='negative')
        return False

def handle_key_enter():
    global user_input, printer_select
    success = False
    if user_input is not None and validate_input(user_input.value):
        if printer_select is not None:
            success = send_zpl_to_printer(zpl_code['value'], printer_select.value)
        else:
            success = send_zpl_to_printer(zpl_code['value'])
        if success:
            user_input.set_value('')

def handle_key(event):
    global user_input, printer_select
    if event.action.keyup:
        if event.key.enter:
            handle_key_enter()

def root():
    global zpl_preview_image_data, user_input, printer_select
    user_input = ui.input(
        placeholder='Original Barcode',
        on_change=lambda e: update_zpl(e.value),
        validation={'Invalid Barcode': lambda x: x is None or len(x) == 0 or validate_input(x)})
    user_input.on('keydown.enter', handle_key_enter)
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
    ui.label("Label Preview:").style('font-size: 120%')
    zpl_preview = ui.image().style('width: 400px; height: 200px; border: 1px solid black;')
    ui_images['zpl_preview'] = zpl_preview
    zpl_preview.bind_source_from(zpl_preview_image_data)
    printer_select_local: ui.select = ui.select(get_printers(),
                               label='Select Printer',
                               value=win32print.GetDefaultPrinter())
    printer_select = printer_select_local
    with ui.button(icon="print",
              on_click=lambda: send_zpl_to_printer(zpl_code['value'], printer_select_local.value)) as print_button:
        print_button.props("size=xl")
        print_button.bind_enabled_from(user_input, 'value', validate_input)
        ui.tooltip("Print (shortcut key: Enter)").classes('text-xs')
    ui.keyboard(on_key=handle_key)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='enable debug mode')
    return parser.parse_args()

# Main
args = parse_args()
if args.debug:
    debug_mode = True

window_size=(500, 605)
if debug_mode:
    window_size = None
ui.run(root=root,
       title="Royal Papworth Hospital Barcode Printing Ver (2.00)",
       window_size=window_size,
       favicon="🖨️",
       reload=debug_mode)
