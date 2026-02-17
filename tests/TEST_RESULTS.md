# Test run: pytest

Commands run (PowerShell):

```powershell
d:
cd 'd:\Programy\7kStudio\Deadalus'
$env:QT_QPA_PLATFORM='offscreen'
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```

Summary
-------

All tests executed; 3 tests failed (see output below).

Captured pytest output
----------------------

```
FFF                                                                      [100%]
================================== FAILURES ===================================
_______________________ test_new_airfoil_calls_tree_add _______________________

monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001FF09093A90>

    def test_new_airfoil_calls_tree_add(monkeypatch):
        make_qapp()
        mb_mod = importlib.import_module('src.arfdes.menu_bar')
        MenuBar = mb_mod.MenuBar
    
>       mb = object.__new__(MenuBar)
             ^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: object.__new__(MenuBar) is not safe, use MenuBar.__new__()

tests\test_menu_bar.py:81: TypeError
________________ test_append_airfoil_appends_and_updates_tree _________________

tmp_path = WindowsPath('C:/Users/jakub/AppData/Local/Temp/pytest-of-jakub/pytest
-0/test_append_airfoil_appends_an0')                                            monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001FF09090D50>

    def test_append_airfoil_appends_and_updates_tree(tmp_path, monkeypatch):
        make_qapp()
        mb_mod = importlib.import_module('src.arfdes.menu_bar')
        MenuBar = mb_mod.MenuBar
    
>       mb = object.__new__(MenuBar)
             ^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: object.__new__(MenuBar) is not safe, use MenuBar.__new__()   

tests\test_menu_bar.py:99: TypeError
________________________ test_save_airfoil_writes_file ________________________ 

tmp_path = WindowsPath('C:/Users/jakub/AppData/Local/Temp/pytest-of-jakub/pytest
-0/test_save_airfoil_writes_file0')                                             monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001FF69D70590>    

    def test_save_airfoil_writes_file(tmp_path, monkeypatch):
        make_qapp()
        mb_mod = importlib.import_module('src.arfdes.menu_bar')
        MenuBar = mb_mod.MenuBar

>       mb = object.__new__(MenuBar)
             ^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: object.__new__(MenuBar) is not safe, use MenuBar.__new__()   

tests\test_menu_bar.py:133: TypeError
=========================== short test summary info =========================== 
FAILED tests/test_menu_bar.py::test_new_airfoil_calls_tree_add - TypeError: obje
ct.__new__(MenuBar) is not safe, use MenuBar.__new__()                          FAILED tests/test_menu_bar.py::test_append_airfoil_appends_and_updates_tree - Ty
peError: object.__new__(MenuBar) is not safe, use MenuBar.__new__()             FAILED tests/test_menu_bar.py::test_save_airfoil_writes_file - TypeError: object
.__new__(MenuBar) is not safe, use MenuBar.__new__()                            3 failed in 1.92s
```

Quick diagnosis and next steps
------------------------------

- Failure cause: tests use `object.__new__(MenuBar)` which raises `TypeError` for PyQt classes. Use one of these fixes:
  - Instantiate normally with a minimal `QApplication` and suitable dummy args, or
  - Create the instance via `MenuBar.__new__(MenuBar)` and then call `MenuBar.__init__(mb, program=..., project=..., parent=..., time=None)`, or
  - Refactor tests to use a thin wrapper or factory that constructs `MenuBar` safely.

- I can update `tests/test_menu_bar.py` to use `MenuBar.__new__(MenuBar)` plus a proper `__init__` call, or to construct a real `MenuBar` with dummy `program`/`project`/`parent` objects. Tell me which option you prefer and I'll patch the tests.
