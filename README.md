# Barcode Printing for Blood Products

This is an unofficial Windows application made to convert barcode serials into the ISTB 128 standard format for Blood Products for the Royal Papworth Hospital Blood Transfusion department, UK. This can then be sent to a Zebra label printer.

![Demo](./readme_assets/demo.webp)

## Developer Dependencies

The dependencies can be installed with the requirements.txt file via the following command:
```
pip install -r requirements.txt
```

* Python (3.10+)
* Python modules:
    * pywin32
    * nicegui (3.00+)
    * requests
    * pywebview
    * pyinstaller

## Usage
See the GitHub releases page for the latest downloaded executable files. The .exe files avoids having to install any dependencies.

The app can also be ran if you have a Python interpreter installed on your machine via running the following command in a Windows Terminal:
```
python .\BCPrinter.py
```

## Info for developers
### Packaging
The NiceGUI Python framework bundles a command called `nicegui-pack` for packaging the application into a standalone executable file.

A convenience PowerShell script can be found in the repository for bundling the application. You can run the following in the terminal, and the .exe file will be built into the `dist` folder:

```
.\package.ps1
```

Alternatively you can run directly the following `nicegui-pack` command to package the app, and the .exe file will be built into the `dist` folder:

```
nicegui-pack --onefile --windowed --icon favicon.ico  --name "BCPrinter" .\BCPrinter.py
```