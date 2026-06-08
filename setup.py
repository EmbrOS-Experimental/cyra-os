import os
import sys
import subprocess
import shutil
from pathlib import Path

# Config
APP_NAME = "Cyra-OS"
BASE_DIR = Path(__file__).parent
VENV_DIR = BASE_DIR / "venv"
PYTHON_EXE = VENV_DIR / "Scripts" / "python.exe" if os.name == "nt" else VENV_DIR / "bin" / "python"

def print_step(msg):
    print(f"\n[🚀] {msg}...")

def run_command(cmd, cwd=None):
    try:
        subprocess.run(cmd, check=True, cwd=cwd)
    except Exception as e:
        print(f"❌ Eroare la execuția comenzii: {e}")
        sys.exit(1)

def main():
    print("="*60)
    print(f"       BOOTSTRAP: {APP_NAME.upper()} — HIGH-FIDELITY SETUP")
    print("="*60)

    # 1. Create VENV
    if not VENV_DIR.exists():
        print_step("Creare mediu virtual (venv)")
        run_command([sys.executable, "-m", "venv", str(VENV_DIR)])
    else:
        print_step("Mediul virtual există deja")

    # 2. Upgrade PIP
    print_step("Actualizare manager pachete (pip)")
    run_command([str(PYTHON_EXE), "-m", "pip", "install", "--upgrade", "pip"])

    # 3. Install Requirements
    print_step("Instalare module necesare (LiteLLM, FastAPI, etc.)")
    run_command([str(PYTHON_EXE), "-m", "pip", "install", "-r", "requirements.txt"])

    # 4. Initialize Local Directories
    print_step("Configurare structură de date")
    for folder in ["brain", "skills", "plugins", "config"]:
        (BASE_DIR / folder).mkdir(exist_ok=True)

    # 5. Create CLI Shim (cyra.bat)
    print_step("Configurare comandă globală 'cyra'")
    shim_path = BASE_DIR / "cyra.bat"
    shim_content = f"@echo off\n\"{str(PYTHON_EXE)}\" \"{str(BASE_DIR / 'manage.py')}\" %*"
    shim_path.write_text(shim_content)

    # 6. Success
    print("\n" + "✨"*20)
    print("  CYRA-OS ESTE PREGĂTITĂ 100%!")
    print("✨"*20)
    print(f"\nUtilizează fișierul 'cyra.bat' pentru a gestiona sistemul.")
    print("\nComenzi disponibile:")
    print("  ./cyra.bat start   - Pornește serverul și workspace-ul")
    print("  ./cyra.bat setup   - Configurează cheia API și identitatea")
    print("  ./cyra.bat status  - Verifică starea sistemului")
    print("\nDeschide workspace-ul la: http://localhost:8200")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
