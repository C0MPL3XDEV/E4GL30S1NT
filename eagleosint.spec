from PyInstaller.utils.hooks import collect_all

datas_lxml,    binaries_lxml,    hiddenimports_lxml    = collect_all("lxml")
datas_certifi, binaries_certifi, hiddenimports_certifi = collect_all("certifi")
datas_pkg,     binaries_pkg,     hiddenimports_pkg     = collect_all("eagleosint")

a = Analysis(
    ["E4GL30S1NT.py"],
    pathex=[],
    binaries=binaries_lxml + binaries_certifi + binaries_pkg,
    datas=datas_lxml + datas_certifi + datas_pkg,
    hiddenimports=(
        hiddenimports_lxml
        + hiddenimports_certifi
        + hiddenimports_pkg
        + [
            "googlesearch",
            "tabulate",
            "bs4",
            "click",
        ]
    ),
    hookspath=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="eagleosint",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
)