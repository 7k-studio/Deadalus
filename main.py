import sys
# Redirect stdout and stderr to a log file
log_file = open("toolout.log", "w")
sys.stdout = log_file
sys.stderr = log_file

from PyQt5.QtWidgets import QApplication
from src.splash.splash_screen import SplashScreen
import src.globals as globals

def main():
    app = QApplication(sys.argv)

    splash = SplashScreen(globals.AIRFLOW)
    splash.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()