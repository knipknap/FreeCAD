# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2024 FreeCAD Team                                       *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

"""Command definitions for the BitLibrary UI integration."""

from PySide.QtCore import QT_TRANSLATE_NOOP
import FreeCAD
import FreeCADGui
import Path.Preferences

# Note: Using relative imports assuming this file is inside BitLibrary
from .db import ToolDB
from .serializers.fcserializer import FCSerializer
from .ui.library import LibraryUI
from .i18n import install_translator

# Global instance to hold the UI window to prevent it from being garbage collected
# and to allow toggling visibility if needed in the future.
_library_ui_instance = None


class CommandBitLibraryOpen:
    """
    Command to open the BitLibrary editor.
    """

    def GetResources(self):
        """Return command resources."""
        # TODO: Use a dedicated icon for the new library
        return {
            "Pixmap": "CAM_ToolTable",
            "MenuText": QT_TRANSLATE_NOOP("CAM_BitLibraryOpen", "Tool Library editor"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "CAM_BitLibraryOpen", "Open an editor to manage tool libraries"
            ),
            "CmdType": "ForEdit",
        }

    def IsActive(self):
        """Return true if the command should be active."""
        # Command is active if a document is open
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        """Execute the command."""
        global _library_ui_instance

        # Prevent opening multiple instances
        if _library_ui_instance and _library_ui_instance.form.isVisible():
            _library_ui_instance.form.raise_()
            _library_ui_instance.form.activateWindow()
            return

        try:
            # 1. Get the library path from preferences
            library_path = Path.Preferences.lastPathToolLibrary()
            if not library_path:
                # Handle case where path might not be set (should default, but safety check)
                FreeCAD.Console.PrintError("Tool Library path not configured correctly.\n")
                return

            # 2. Instantiate Serializer and ToolDB
            serializer = FCSerializer(library_path)
            tool_db = ToolDB()

            # 3. Load data from storage
            # Use try-except blocks for robustness in case of loading errors
            try:
                tool_db.deserialize_machines(serializer)
            except Exception as e:
                FreeCAD.Console.PrintWarning(f"Failed to load machines: {e}\n")
            try:
                tool_db.deserialize_shapes(serializer)
            except Exception as e:
                FreeCAD.Console.PrintWarning(f"Failed to load shapes: {e}\n")
            try:
                tool_db.deserialize_tools(serializer) # Must be before libraries
            except Exception as e:
                FreeCAD.Console.PrintWarning(f"Failed to load tools: {e}\n")
            try:
                tool_db.deserialize_libraries(serializer)
            except Exception as e:
                FreeCAD.Console.PrintWarning(f"Failed to load libraries: {e}\n")


            # 4. Instantiate and show the UI
            # Pass the main window as parent
            main_win = FreeCADGui.getMainWindow()
            _library_ui_instance = LibraryUI(tool_db, serializer, parent=main_win)
            _library_ui_instance.form.show()
            _library_ui_instance.form.activateWindow() # Bring it to the front

        except Exception as e:
            FreeCAD.Console.PrintError(f"Failed to open BitLibrary UI: {e}\n")
            # Ensure instance is cleared on error
            _library_ui_instance = None


# Register the command only if running in GUI mode
if FreeCAD.GuiUp:
    FreeCADGui.addCommand("CAM_BitLibraryOpen", CommandBitLibraryOpen())

# Define lists for menu/toolbar integration (can be adjusted later)
BarList = ["CAM_BitLibraryOpen"]
MenuList = ["CAM_BitLibraryOpen"]

FreeCAD.Console.PrintLog("Loading BitLibrary Commands... done\n")