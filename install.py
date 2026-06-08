import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    print("\n" + "="*60)
    print("      ✨ CYRA-OS v1.0 — EXPERIENȚA DE SETUP ✨")
    print("="*60)
    print("Bine ai venit, Robert. Hai să configurăm sistemul tău Cyra-OS.\n")

def check_step(name):
    print(f"🔄 Verificare: {name}...", end="", flush=True)
    time.sleep(0.5)

def success():
    print(" ✅ OK")

def fail(msg):
    print(" ❌ EȘUAT")
    print(f"\n[!] Eroare: {msg}")
    sys.exit(1)

def run_install():
    print_banner()

    # 1. Verificare Python
    check_step("Versiune Python")
    if sys.version_info >= (3, 10):
        success()
    else:
        fail("Cyra-OS necesită Python 3.10 sau mai nou.")

    # 2. Verificare FFmpeg
    check_step("Dependență FFmpeg")
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        success()
    except:
        fail("FFmpeg nu este instalat sau nu este în PATH. Este necesar pentru voce.")

    # 3. Instalare Dependențe
    print("\n📦 Instalăm librăriile necesare (poate dura puțin)...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Librării instalate cu succes.")
    except Exception as e:
        fail(f"Nu s-au putut instala dependențele: {e}")

    # 4. Configurare API Key
    print("\n🔑 CONFIGURARE OPENROUTER")
    print("Cyra are nevoie de o cheie API pentru a gândi.")
    api_key = input("Introdu cheia ta OpenRouter API: ").strip()
    
    if not api_key:
        print("⚠️ Atenție: Nu ai introdus o cheie. Va trebui să o adaugi manual în .env ulterior.")
    
    env_content = f"OPENROUTER_API_KEY={api_key}\n"
    Path(".env").write_text(env_content)
    print("✅ Fișierul .env a fost creat.")

    # 5. Inițializare Bază de Date
    check_step("Sistem de Memorie")
    try:
        from brain.memory import memory
        success()
    except Exception as e:
        fail(f"Nu s-a putut inițializa sistemul de memorie: {e}")

    # 6. Finalizare
    print("\n" + "="*60)
    print("🎉 SETUP FINALIZAT CU SUCCES!")
    print("="*60)
    print("\nPentru a porni Cyra-OS, rulează:")
    print(">> python server.py")
    print("\nApoi deschide în browser: http://localhost:8200")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    run_install()
