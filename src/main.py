from PyQt5.QtWidgets import QApplication
import sys
from splash.splash_screen import SplashScreen
import globals

def main():
    app = QApplication(sys.argv)

    splash = SplashScreen(globals.AIRFLOW)
    splash.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()