import os
import shutil
import subprocess
import sys

def build_game():
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Define the spec file content for one-directory package
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['dd.py'],
    pathex=[],
    binaries=[],
    datas=[],  # Empty datas list since we'll add assets manually
    hiddenimports=[
        'tensorflow',
        'cv2',
        'numpy',
        'pygame',
        'textwrap',
        'threading',
        'tensorflow.lite',
        'tensorflow.lite.python.interpreter'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MathRunnerGame',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='Assets/icon.ico' if os.path.exists('Assets/icon.ico') else None,
)

# Create a one-directory bundle (not onefile)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MathRunnerGame'
)
"""
    
    # Write the spec file
    with open('game.spec', 'w') as f:
        f.write(spec_content)
    
    # Run PyInstaller to create one-directory package
    # Remove the --onedir flag when using a spec file
    try:
        subprocess.check_call(['pyinstaller', 'game.spec'])
        print("Build successful! Application is in the 'dist/MathRunnerGame' folder.")
        
        # Instructions for manual asset copying
        print("\n" + "="*50)
        print("MANUAL ASSET SETUP INSTRUCTIONS:")
        print("="*50)
        print("1. Navigate to: dist/MathRunnerGame/")
        print("2. Create an 'Assets' folder")
        print("3. Copy all your asset folders into the Assets folder:")
        print("   - Emotion detection models")
        print("   - Buttons")
        print("   - Backgrounds")
        print("   - Floor")
        print("   - Fonts")
        print("   - Player")
        print("   - Enemy")
        print("   - Questions")
        print("   - Gameover")
        print("   - option")
        print("   - Menu")
        print("   - Sounds")
        print("4. Your final structure should be:")
        print("   dist/MathRunnerGame/")
        print("   ├── MathRunnerGame.exe")
        print("   ├── [other .dll and .pyd files]")
        print("   └── Assets/")
        print("       ├── Emotion detection models/")
        print("       ├── Buttons/")
        print("       └── ... etc.")
        print("="*50)
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    build_game()
    