'''

Copyright (C) 2025 Jakub Kamyk

This file is part of AirFLOW.

AirFLOW is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

AirFLOW is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with AirFLOW.  If not, see <http://www.gnu.org/licenses/>.

'''

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

