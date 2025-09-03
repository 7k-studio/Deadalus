# AirFoil & Lifting Objects Workbench AirFLOW

This project is a CAD software whitch allows user to create an airfoil from scratch, or match it with reference, and to create wing out of created airfoils.
Project consists of two modules:
1. Airfoil designer - for airfoil operations
2. Wing Workbench - for wing creation and modification
   
AirFLOW implements a 3D OpenGL viewport embedded in a PyQt5 GUI. The application allows for mouse interaction to translate, rotate, and zoom within the 3D space. It features a structured layout with a tree menu for navigation, a dropdown menu for basic functions, and a table widgets for user interaction.

## Project Structure

```
AirFLOW
├── src
│   ├── main.py                # Entry point of the application
|   ├── preferences.py
|   ├── globals.py
|   ├── arfdes
|   |   ├── airfoil_designer.py
|   |   ├── menu_bar.py
|   |   ├── plot_canvas.py
|   |   └── widget_tabele.py
|   ├── data
|   ├── images
|   ├── obj
|   |   ├── aero.py
|   |   └── car.py
|   ├── opengl
|   |   ├── bckgrd.py
|   |   ├── shapes.py
|   |   ├── test_cube.py
│   │   ├── viewport.py        # OpenGL viewport handling
│   │   └── shaders
│   │       ├── vertex_shader.glsl   # Vertex shader code
│   │       └── fragment_shader.glsl # Fragment shader code
|   ├── splash
|   ├── utils
|   |   ├── dxf.py
|   |   ├── step.py
|   |   ├── tools_airfoil.py
|   |   ├── tools_program.py
|   |   ├── tools_wing.py
│   |   └── helpers.py         # Utility functions and helpers
│   ├── wngwb
│   │   ├── main_window.py     # Main window layout and setup
│   │   ├── tree_menu.py       # Tree menu for navigation
│   │   ├── console_widget.py   # Command-line-like interface for user input
│   │   └── menu_bar.py        # Dropdown menu for file operations
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Setup Instructions

1. Clone the repository or download the project files.
2. Navigate to the project directory.
3. Install the required dependencies using pip:

   ```
   pip install -r requirements.txt
   ```

4. Run the application:

   ```
   python src/main.py
   ```

## Setup for MAC OS

1. prerequisites: Homebrew
2. `brew install python`
3. `python3 -m venv myenv`
4. `source myenv/bin/activate`
5. `pip3 install -r requirements.txt`
6. `python3 src/main.py`

## Features

- MatPlotLib graphics for Airfoil Designer
- 3D OpenGL viewport with mouse interaction for:
  - Translation
  - Rotation
  - Zoom
- Tree menu for easy navigation of application components.
- Dropdown menu with basic file operations (New, Save, etc.).

## Usage

Once the application is running, you can interact with the 3D viewport using the mouse. Use the tree menu to navigate through different components of the application, and utilize the console widget for input and feedback.

## License

This project is licensed under the GNU License. See the LICENSE file for more details.
