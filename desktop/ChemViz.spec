# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=['.'],
    binaries=[],
    datas=[('styles', 'styles')],
    hiddenimports=['main_window', 'widgets', 'widgets.header', 'widgets.sidebar', 'widgets.main_content', 'widgets.csv_upload', 'widgets.summary_screen', 'widgets.auth_dialog', 'widgets.history_screen', 'widgets.dataset_history', 'widgets.kpi_cards', 'widgets.data_table', 'charts', 'charts.charts', 'charts.chart_config', 'core', 'core.api_client', 'core.tokens', 'config', 'config.pdf_generator', 'config.pdf_report_config'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'tensorflow', 'transformers', 'ultralytics', 'torchvision', 'cv2', 'jupyter', 'notebook', 'IPython', 'pygame', 'boto3', 'botocore', 'timm', 'onnxruntime', 'h5py', 'av', 'shapely'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ChemViz',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
