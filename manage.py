import os
import sys
import argparse
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent

def start_server():
    print("[🚀] Pornim Cyra-OS...")
    try:
        # Check if venv exists
        venv_python = BASE_DIR / "venv" / "Scripts" / "python.exe"
        if not venv_python.exists():
            print("❌ Eroare: Mediul virtual nu a fost găsit. Rulează 'python setup.py' mai întâi.")
            return

        subprocess.run([str(venv_python), str(BASE_DIR / "server.py")])
    except KeyboardInterrupt:
        print("\n[👋] Cyra-OS a fost oprită.")

def setup_config():
    print("\n" + "="*40)
    print("      CONFIGURARE CYRA-OS")
    print("="*40)
    
    api_key = input("Introdu cheia ta OpenRouter API: ").strip()
    if api_key:
        env_file = BASE_DIR / ".env"
        env_file.write_text(f"OPENROUTER_API_KEY={api_key}\n")
        print("✅ Cheia API a fost salvată.")
    
    print("\nConfigurație finalizată.")

def check_status():
    print("\n--- STATUS CYRA-OS ---")
    print(f"Director: {BASE_DIR}")
    print(f"Venv: {'✅ Prezent' if (BASE_DIR / 'venv').exists() else '❌ Lipsă'}")
    print(f"Config: {'✅ Prezent' if (BASE_DIR / '.env').exists() else '❌ Lipsă'}")
    print(f"Memorie: {'✅ Inițializată' if (BASE_DIR / 'brain' / 'cyra_memory.db').exists() else '⏳ La prima pornire'}")
    print("----------------------")

def main():
    parser = argparse.ArgumentParser(description="Cyra-OS Management CLI")
    parser.add_argument("command", choices=["start", "setup", "status"], help="Comanda de executat")
    
    args = parser.parse_args()
    
    if args.command == "start":
        start_server()
    elif args.command == "setup":
        setup_config()
    elif args.command == "status":
        check_status()

if __name__ == "__main__":
    main()
