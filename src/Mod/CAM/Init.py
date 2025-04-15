# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2014 Yorik van Havre <yorik@uncreated.net>              *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   FreeCAD is distributed in the hope that it will be useful,            *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Lesser General Public License for more details.                   *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with FreeCAD; if not, write to the Free Software        *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

import os
import FreeCAD


FreeCAD.__unit_test__ += ["TestCAMApp"]

# This code handles parameter groups following the CAM workbench renaming
# (PATH -> CAM). This code can be removed after the 1.0 release.
ParGrpSys = FreeCAD.ParamGet("System parameter:Modules").GetGroup("Path")
if ParGrpSys.HasGroup("CAM"):
    pass
elif ParGrpSys.HasGroup("Path"):
    ParGrpSys.RenameGroup("Path", "CAM")

ParGrpUser = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Path")
parent = ParGrpUser.Parent()
if parent.HasGroup("CAM"):
    pass
elif parent.HasGroup("Path"):
    result = parent.RenameGroup("Path", "CAM")

# Get the Parameter Group of this module (using the potentially renamed group)
ParGrp = FreeCAD.ParamGet("System parameter:Modules").GetGroup("CAM")

# Set the needed information
ParGrp.SetString("HelpIndex", "Path/Help/index.html")
ParGrp.SetString("WorkBenchName", "CAM")
ParGrp.SetString("WorkBenchModule", "PathWorkbench.py")

