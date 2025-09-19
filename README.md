# Deadalus

This project is a free CAD software whitch allows user to create an airfoil from scratch, or match it with reference, and to create wing out of created airfoils.
Program consists of two modules:
1. Airfoil designer - for airfoil operations
2. Wing Workbench - for wing creation and modification
   
Deadalus implements a 3D OpenGL viewport embedded in a PyQt5 GUI. The application allows for mouse interaction to translate, rotate, and zoom within the 3D space. It features a structured layout with a tree menu for navigation, a dropdown menu for basic functions, and a table widgets for user interaction.

## Project Structure

```
Deadalus
├── main.py                      # Entry point of the application
├── src
│   ├── settings                 # Store for user settings
|   ├── preferences.py           # Loads / Saves / Changes settngs
|   ├── globals.py               # Classes for whole program to work
|   ├── arfdes
|   |   ├── airfoil_designer.py  # Main window layout and setup
|   |   ├── fit_2_reference.py   # Experimental function for reference matching
|   |   ├── menu_bar.py          # Dropdown menu for file operations
|   |   ├── plot_canvas.py       # Obsolete viewport
|   |   ├── tools_airfoil.py     # Utility functions and helpers
|   |   ├── widget_tabele.py     # Tabele for object properties
|   |   └── widget_tree.py       # Tree menu for objects store
|   |
|   ├── assets                   # Storage for user manual and images
|   ├── data                     # Storage for reference and established files
|   ├── obj
|   |   ├── car.py               # Classes for reference
|   |   ├── draw_construction.py # Helper
|   |   ├── objects2D.py         # Classes for 2D objects
|   |   └── objects3D.py         # Classes for 3D objects
|   ├── opengl
|   |   ├── bckgrd.py            # OpenGL functions for 3D drawings
|   |   ├── construction.py      # OpenGL functions for 3D drawings
|   |   ├── solid.py             # OpenGL functions for 3D drawings
|   |   ├── test_cube.py         # OpenGL functions for 3D drawings
│   │   ├── viewport2D.py        # OpenGL viewport for Airfoil Designer
│   │   ├── viewport3D.py        # OpenGL viewport for Wing Designer
│   │   ├── wireframe.py         # OpenGL functions for 3D drawings
│   │   └── shaders
│   │       ├── vertex_shader.glsl   # Vertex shader code
│   │       └── fragment_shader.glsl # Fragment shader code
|   ├── splash
│   │   └── splash_screen.py    # Welcome screen on program init
|   ├── utils
|   |   ├── dxf.py              # DXF  export script
|   |   ├── step.py             # STEP export script
│   |   └── tools_program.py    # Utility functions and helpers
│   └── wngwb
│       ├── console_widget.py   # Command-line-like interface for user input
│       ├── main_window.py      # Main window layout and setup
│       ├── menu_bar.py         # Dropdown menu for file operations
│       ├── menu_context.py     # Future pleaceholder for context menu
│       ├── tools_wing.py       # Utility functions and helpers
│       ├── widget_tabele.py    # Tabele for object properties
│       └── widget_tree.py      # Tree menu for objects store    
├── .venv
├── requirements.txt            # Program dependencies
├── LICENSE                     # Program licence
├── logo.ico                    # Program logo
└── README.md                   # Program documentation
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

- 2D OpenGl viewport with mouse interaction for Airfoil Designer
  - Translation
  - Zoom
- 3D OpenGL viewport with mouse interaction for Wing designer:
  - Translation
  - Rotation
  - Zoom
- Tree menu for easy navigation of application components.
- Dropdown menu with basic file operations (New, Save, etc.).

## Usage

Once the application is running, you can create a parametric airfoil and wing design. Use interactive tabele of parameters to modify the objects. Interact with the 2D/3D viewport using the mouse to preview created objects. Use the tree menu to navigate through different components of the application. Use export functions to save project to standard CAD format like: .dxf and .step. Use save button to save current state of the project within Deadalus program. 

## License

This project is licensed under the GNU License. See the LICENSE file for more details.
