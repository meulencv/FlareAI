import argparse
import getpass
import os
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="Arranca Traffic Lab y HappyRobot sin guardar la API key")
    parser.add_argument("--local", action="store_true", help="Solo detector local, sin HappyRobot")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    python = ROOT / (".venv/Scripts/python.exe" if os.name == "nt" else ".venv/bin/python")
    if not python.exists():
        subprocess.run([sys.executable, "-m", "venv", str(ROOT / ".venv")], check=True)
    check = subprocess.run([str(python), "-c", "import cv2,numpy,tzdata"], capture_output=True)
    if check.returncode:
        subprocess.run([str(python), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")], check=True)
    environment = os.environ.copy()
    if args.local:
        environment.pop("HAPPYROBOT_API_KEY", None)
    else:
        key = environment.get("HAPPYROBOT_API_KEY") or getpass.getpass("API key de HappyRobot (oculta; Enter para modo local): ").strip()
        if key:
            environment["HAPPYROBOT_API_KEY"] = key
    if not environment.get("HAPPYROBOT_API_KEY"):
        subprocess.run([str(python), str(ROOT / "prepare.py")], check=True, cwd=ROOT)
    if not args.no_browser:
        timer = threading.Timer(2, lambda: webbrowser.open("http://127.0.0.1:8790"))
        timer.daemon = True
        timer.start()
    subprocess.run([str(python), str(ROOT / "server.py")], env=environment, check=True, cwd=ROOT)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
