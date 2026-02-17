import os
import sys
import types
import json
import pytest

PyQt5 = pytest.importorskip("PyQt5")
from PyQt5.QtWidgets import QApplication

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import importlib


def make_qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app


class DummyTree:
    def __init__(self):
        self.add_called = False
        self.add_airfoil_called = False
        self.deleted = False
        self._items = []

    def add(self, name, time, desc):
        self.add_called = True

    def add_airfoil_to_tree(self, name, obj=None):
        self.add_airfoil_called = True

    def delete(self):
        self.deleted = True
        return True, "AF1"

    def currentItem(self):
        # return a dummy item object; MenuBar expects indexOfTopLevelItem to work
        return object()

    def indexOfTopLevelItem(self, item):
        return 0

    def selectedItems(self):
        return [type("It", (), {"text": lambda self, i: "AF1"})()]


class DummyProject:
    def __init__(self):
        self.project_airfoils = []

    def new(self):
        pass

    def open(self):
        pass

    def save(self):
        pass

    def save_as(self):
        pass


def setup_globals_module(tmp_project):
    # Create a fake src.globals module and insert into sys.modules as 'globals'
    mod = types.SimpleNamespace()
    mod.PROJECT = tmp_project
    sys.modules['globals'] = mod
    return mod


def test_new_airfoil_calls_tree_add(monkeypatch):
    make_qapp()
    mb_mod = importlib.import_module('src.arfdes.menu_bar')
    MenuBar = mb_mod.MenuBar

    mb = MenuBar.__new__()
    # Inject dependencies without running __init__
    mb.DEADALUS = types.SimpleNamespace(preferences={'general': {'beta_features': False}})
    mb.PROJECT = DummyProject()
    mb.ARFDES = types.SimpleNamespace(TREE_AIRFOIL=DummyTree())
    mb.time = None
    mb.logger = mb_mod.logging.getLogger('test')

    # call method
    mb.newAirfoil()
    assert mb.ARFDES.TREE_AIRFOIL.add_called is True


def test_append_airfoil_appends_and_updates_tree(tmp_path, monkeypatch):
    make_qapp()
    mb_mod = importlib.import_module('src.arfdes.menu_bar')
    MenuBar = mb_mod.MenuBar

    mb = object.__new__(MenuBar)
    mb.DEADALUS = types.SimpleNamespace(preferences={'general': {'beta_features': False}})
    project = DummyProject()
    mb.PROJECT = project
    tree = DummyTree()
    mb.ARFDES = types.SimpleNamespace(TREE_AIRFOIL=tree)
    mb.logger = mb_mod.logging.getLogger('test')

    # Prepare a fake file and fake airfoil object
    fake_file = tmp_path / "af.arf"
    fake_file.write_text('{"infos": {"name": "AF1"}, "top_curve": [], "dwn_curve": [], "params": {}}')

    fake_airfoil = types.SimpleNamespace(infos={"name": "AF1"})

    # Patch file dialog to return our file
    monkeypatch.setattr(mb_mod, 'QFileDialog', types.SimpleNamespace(getOpenFileName=lambda *a, **k: (str(fake_file), None), Options=lambda: None))

    # Patch tools_airfoils.load_airfoil_from_json
    monkeypatch.setattr(mb_mod.tools_airfoils, 'load_airfoil_from_json', lambda fn: (fake_airfoil, None))

    # Ensure globals.PROJECT exists
    setup_globals_module(project)

    mb.appendAirfoil()

    assert project.project_airfoils and project.project_airfoils[-1] == fake_airfoil
    assert tree.add_airfoil_called is True


def test_save_airfoil_writes_file(tmp_path, monkeypatch):
    make_qapp()
    mb_mod = importlib.import_module('src.arfdes.menu_bar')
    MenuBar = mb_mod.MenuBar

    mb = object.__new__(MenuBar)
    project = DummyProject()
    # Create a dummy airfoil object and put it in project
    af = types.SimpleNamespace(infos={"name": "AF1"})
    project.project_airfoils.append(af)
    mb.PROJECT = project
    tree = DummyTree()

    # override currentItem and indexOfTopLevelItem to map to project index 0
    tree.currentItem = lambda: object()
    tree.indexOfTopLevelItem = lambda item: 0

    mb.ARFDES = types.SimpleNamespace(TREE_AIRFOIL=tree)
    mb.logger = mb_mod.logging.getLogger('test')

    # Patch tools_airfoils.save_airfoil_to_json
    sample_json = json.dumps({"infos": {"name": "AF1"}})
    monkeypatch.setattr(mb_mod.tools_airfoils, 'save_airfoil_to_json', lambda idx: sample_json)

    # Patch save file dialog
    out_file = tmp_path / "out.arf"
    monkeypatch.setattr(mb_mod, 'QFileDialog', types.SimpleNamespace(getSaveFileName=lambda *a, **k: (str(out_file), None), Options=lambda: None))

    mb.saveAirfoil()

    assert out_file.exists()
    assert out_file.read_text() == sample_json
