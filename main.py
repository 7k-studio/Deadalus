'''

Copyright (C) 2025 Jakub Kamyk

This file is part of DEADALUS.

DEADALUS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

DEADALUS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with DEADALUS.  If not, see <http://www.gnu.org/licenses/>.

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

    splash = SplashScreen(globals.DEADALUS)
    splash.show()
    
    sys.exit(app.exec_())

def header_old():
    print("      ____________     ___                 _________    ___          ___________     ___           ___  ")
    print("     /  ______   /\   /__/\               /  ______/\  /  /\        /  _____   /\   /  /\         /  /\ ")
    print("    /  /\____/  / /   \__\/  _______     /  /\_____\/ /  / /       /  /\___/  / /  /  / /        /  / / ")
    print("   /  /_/___/  / /  ___     /  ____/\   /  /_/___    /  / /       /  / /  /  / /  /  / / ___    /  / /  ")
    print("  /  ______   / /  /  /\   /  /\___\/  /  ______/\  /  / /       /  / /  /  / /  /  / / /  /\  /  / /   ")
    print(" /  /\____/  / /  /  / /  /  / /      /  /\_____\/ /  /_/____   /  /_/__/  / /  /  /_/_/  /_/_/  / /    ")
    print("/__/ /   /__/ /  /__/ /  /__/ /      /__/ /       /_________/\ /__________/ /  /________________/ /     ")
    print("\__\/    \__\/   \__\/   \__\/       \__\/        \_________\/ \__________\/   \________________\/      ")
    print(" ")
    print(f"Program version: {globals.DEADALUS.program_version}")
    print("|/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\/|")
    print("")
    print(f"Program opened on: {datetime.datetime.now()}")

def header():
    print("       ________        __________    ____________    ________        ____________    ___            ___      ___    ___________  ")
    print("      /  ____  \      /  _______/\  /  ______   /\  /  ____  \      /  ______   /\  /  /\          /  /\    /  /\  /  ________/\ ")
    print("     /  /\___\  \    /  /\______\/ /  /\____/  / / /  /\___\  \    /  /\____/  / / /  / /         /  / /   /  / / /  /\_______\/ ")
    print("    /  / /   /  /\  /  /_/____    /  /_/___/  / / /  / /   /  /\  /  /_/___/  / / /  / /         /  / /   /  / / /  /_/______    ")
    print("   /  / /   /  / / /  _______/\  /  ______   / / /  / /   /  / / /  ______   / / /  / /         /  / /   /  / / /________   /\   ")
    print("  /  / /   /  / / /  /\______\/ /  /\____/  / / /  / /   /  / / /  /\____/  / / /  / /         /  / /   /  / /  \_______/  / /   ")
    print(" /  /_/___/  / / /  /_/_____   /  / /   /  / / /  /_/___/  / / /  / /   /  / / /  /_/______   /  /_/___/  / / _________/  / /    ")
    print("/___________/ / /__________/\ /__/ /   /__/ / /___________/ / /__/ /   /__/ / /___________/\ /___________/ / /___________/ /     ")
    print("\___________\/  \__________\/ \__\/    \__\/  \___________\/  \__\/    \__\/  \___________\/ \___________\/  \___________\/      ")
    print("")
    print("|/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\|")
    print(f"Program version: {globals.DEADALUS.program_version}")
    print(f"Program opened on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    

if __name__ == "__main__":
    header()
    main()