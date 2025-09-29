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
import math
import numpy as np
from geomdl import BSpline, utilities

from src.utils.tools_program import CreateBSpline_3D
import src.globals as globals
import src.obj.objects2D as objects2D

from geomdl import NURBS
from geomdl import tessellate
from geomdl import knotvector

class Component:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.infos = {'name': 'component',
                      'creation_date': '',
                      'modification_date': ''}
        
        self.params = {
            'origin_X': 0,
            'origin_Y': 0,
            'origin_Z': 0,
        }

        self.wings = []

    def move(self, cmp_X:float, cmp_Y:float, cmp_Z:float):

        self.logger.info(f"Moving COMPONENT geometry by X:{cmp_X}, Y:{cmp_Y}, Z:{cmp_Z}...")

        tmp_X = self.params['origin_X'] + cmp_X
        tmp_Y = self.params['origin_Y'] + cmp_Y
        tmp_Z = self.params['origin_Z'] + cmp_Z

        return tmp_X, tmp_Y, tmp_Z
    
    def update(self, dummy1, dummy2, dummy3):
        self.logger.info("Updating COMPONENT...")
        self.logger.info("   This function is pointless :( ")
        #self.params['origin_X'] = 0
        #self.params['origin_Y'] = 0
        #self.params['origin_Z'] = 0

    def transform(self, grandparent_index):

        cmp_X = globals.PROJECT.project_components[grandparent_index].origin_X
        cmp_Y = globals.PROJECT.project_components[grandparent_index].origin_Y
        cmp_Z = globals.PROJECT.project_components[grandparent_index].origin_Z

        self.logger.info("Transforming component...")
        self.params['origin_X'], self.params['origin_Y'], self.params['origin_Z'] = self.move_component(cmp_X, cmp_Y, cmp_Z)
        self.logger.info("Done!")
