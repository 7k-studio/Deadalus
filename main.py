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
# Library import
import logging
import sys
import os
import datetime

# Module-level logger so exception hook can always access a logger
logger = logging.getLogger(__name__)

# PyQt import 
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from src.program.splash_screen import SplashScreen

# In-Program import
# from src.program import DEADALUS

def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # To allow clean exit
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.exit()

def main():
    from src.program.program import Program
    DEADALUS = Program()

    #app = QApplication(sys.argv)
    #icon = QIcon("src/assets/logo.png")
    #app.setWindowIcon(icon)
    #app.setStyleSheet(DEADALUS.buildStyleSheet())

    log_file = 'toolout.log'

    if os.path.exists(log_file):
        os.remove(log_file)

    with open(log_file, "w") as file:
        header(DEADALUS.version, file)
    
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(name)s: %(funcName)s: %(message)s", handlers=[logging.FileHandler("toolout.log"), logging.StreamHandler()])

    sys.excepthook = log_uncaught_exceptions

    DEADALUS.APP = QApplication(sys.argv)
    icon = QIcon("src/assets/logo.png")
    DEADALUS.APP.setWindowIcon(icon)
    DEADALUS.APP.setStyleSheet(DEADALUS.buildStyleSheet())
    DEADALUS.SPLASHSCREEN = SplashScreen(DEADALUS)
    DEADALUS.SPLASHSCREEN.show()

    #splash = SplashScreen(DEADALUS)
    #splash.show()
    
    # sys.exit(app.exec_())
    sys.exit(DEADALUS.APP.exec_())

def header(version, file):
    file.write("       _______        _________    ___________    _______        ___________    ___           ___     ___    __________  \n")
    file.write("      /  ___  \      /  ______/\  /  _____   /\  /  ___  \      /  _____   /\  /  /\         /  /\   /  /\  /  _______/\ \n")
    file.write("     /  /\__\  \    /  /\_____\/ /  /\___/  / / /  /\__\  \    /  /\___/  / / /  / /        /  / /  /  / / /  /\______\/ \n")
    file.write("    /  / /  /  /\  /  /_/___    /  /_/__/  / / /  / /  /  /\  /  /_/__/  / / /  / /        /  / /  /  / / /  /_/_____    \n")
    file.write("   /  / /  /  / / /  ______/\  /  _____   / / /  / /  /  / / /  _____   / / /  / /        /  / /  /  / / /_______   /\   \n")
    file.write("  /  / /  /  / / /  /\_____\/ /  /\___/  / / /  / /  /  / / /  /\___/  / / /  / /        /  / /  /  / /  \______/  / /   \n")
    file.write(" /  /_/__/  / / /  /_/____   /  / /  /  / / /  /_/__/  / / /  / /  /  / / /  /_/_____   /  /_/__/  / / ________/  / /    \n")
    file.write("/__________/ / /_________/\ /__/ /  /__/ / /__________/ / /__/ /  /__/ / /__________/\ /__________/ / /__________/ /     \n")
    file.write("\__________\/  \_________\/ \__\/   \__\/  \__________\/  \__\/   \__\/  \__________\/ \__________\/  \__________\/      \n")
    file.write("\n")
    file.write("|/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\|\n")
    file.write(f"Program version: {version}\n")
    file.write(f"Program opened on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    

if __name__ == "__main__":

    # log_file = 'toolout.log'

    # if os.path.exists(log_file):
    #     os.remove(log_file)

    # with open(log_file, "w") as file:
    #     header(DEADALUS, file)
    
    # logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(name)s: %(funcName)s: %(message)s", handlers=[logging.FileHandler("toolout.log"), logging.StreamHandler()])
    # logger = logging.getLogger(__name__)

    # sys.excepthook = log_uncaught_exceptions

    main()