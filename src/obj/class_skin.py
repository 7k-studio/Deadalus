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

from geomdl import NURBS
from geomdl import tessellate
from geomdl import knotvector
from src.obj.objects3D import Surface

class Skin:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = 'Skin'
        self.infos = {'creation_date': '',
                      'modification_date': ''}
        
        self.anchor = 'G0' # G1 or G2 later add 'segment'

        self.LE = Surface()
        self.PS = Surface()
        self.SS = Surface()
        self.TE = Surface()