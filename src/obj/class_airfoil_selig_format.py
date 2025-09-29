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

from src.arfdes.tools_airfoil import CreateBSpline
import src.globals as globals

class Airfoil_selig_format:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.infos = {'name': 'N/A'}
        self.format = 'selig'
        self.top_curve = []
        self.dwn_curve = []