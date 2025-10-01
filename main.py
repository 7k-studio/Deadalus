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
import logging
import sys
import os

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

def header(file):
    file.write("       ________        __________    ____________    ________        ____________    ___            ___      ___    ___________  \n")
    file.write("      /  ____  \      /  _______/\  /  ______   /\  /  ____  \      /  ______   /\  /  /\          /  /\    /  /\  /  ________/\ \n")
    file.write("     /  /\___\  \    /  /\______\/ /  /\____/  / / /  /\___\  \    /  /\____/  / / /  / /         /  / /   /  / / /  /\_______\/ \n")
    file.write("    /  / /   /  /\  /  /_/____    /  /_/___/  / / /  / /   /  /\  /  /_/___/  / / /  / /         /  / /   /  / / /  /_/______    \n")
    file.write("   /  / /   /  / / /  _______/\  /  ______   / / /  / /   /  / / /  ______   / / /  / /         /  / /   /  / / /________   /\   \n")
    file.write("  /  / /   /  / / /  /\______\/ /  /\____/  / / /  / /   /  / / /  /\____/  / / /  / /         /  / /   /  / /  \_______/  / /   \n")
    file.write(" /  /_/___/  / / /  /_/_____   /  / /   /  / / /  /_/___/  / / /  / /   /  / / /  /_/______   /  /_/___/  / / _________/  / /    \n")
    file.write("/___________/ / /__________/\ /__/ /   /__/ / /___________/ / /__/ /   /__/ / /___________/\ /___________/ / /___________/ /     \n")
    file.write("\___________\/  \__________\/ \__\/    \__\/  \___________\/  \__\/    \__\/  \___________\/ \___________\/  \___________\/      \n")
    file.write("\n")
    file.write("|/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\|\n")
    file.write(f"Program version: {globals.DEADALUS.program_version}\n")
    file.write(f"Program opened on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # To allow Ctrl+C clean exit
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.exit()

if __name__ == "__main__":

    log_file = 'toolout.log'

    if os.path.exists(log_file):
        os.remove(log_file)

    with open(log_file, "w") as file:
        header(file)
    
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(name)s: %(funcName)s: %(message)s", handlers=[logging.FileHandler("toolout.log"), logging.StreamHandler()])
    logger = logging.getLogger(__name__)

    sys.excepthook = log_uncaught_exceptions

    main()