import sys
# Redirect stdout and stderr to a log file
#log_file = open("toolout.log", "w")
#sys.stdout = log_file
#sys.stderr = log_file

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from src.splash.splash_screen import SplashScreen
import src.globals as globals
import datetime

def main():
    app = QApplication(sys.argv)

    icon = QIcon("src/assets/logo.png")
    app.setWindowIcon(icon)

    splash = SplashScreen(globals.AIRFLOW)
    splash.show()
    
    sys.exit(app.exec_())

def header():
    print("      ____________     ___                 _________    ___          ___________     ___           ___  ")
    print("     /  ______   /\   /__/\               /  ______/\  /  /\        /  _____   /\   /  /\         /  /\ ")
    print("    /  /\____/  / /   \__\/  _______     /  /\_____\/ /  / /       /  /\___/  / /  /  / /        /  / / ")
    print("   /  /_/___/  / /  ___     /  ____/\   /  /_/___    /  / /       /  / /  /  / /  /  / / ___    /  / /  ")
    print("  /  ______   / /  /  /\   /  /\___\/  /  ______/\  /  / /       /  / /  /  / /  /  / / /  /\  /  / /   ")
    print(" /  /\____/  / /  /  / /  /  / /      /  /\_____\/ /  /_/____   /  /_/__/  / /  /  /_/_/  /_/_/  / /    ")
    print("/__/ /   /__/ /  /__/ /  /__/ /      /__/ /       /_________/\ /__________/ /  /________________/ /     ")
    print("\__\/    \__\/   \__\/   \__\/       \__\/        \_________\/ \__________\/   \________________\/      ")
    print(" ")
    print(f"Program version: {globals.AIRFLOW.program_version}")
    print("|/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\/|")
    print("")
    print(f"Program opened on: {datetime.datetime.now()}")
    

if __name__ == "__main__":
    header()
    main()

