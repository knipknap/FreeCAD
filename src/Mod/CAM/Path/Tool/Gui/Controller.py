# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2019 sliptonic <shopinthewoods@gmail.com>               *
# *   Copyright (c) 2024 FreeCAD Team (Restored from oldcontroller.py)      *
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

from PySide import QtCore, QtGui
import FreeCAD
import FreeCADGui
import Path
import Path.Base.Gui.Util as PathGuiUtil
import Path.Tool.Controller as PathToolController

translate = FreeCAD.Qt.translate

class ViewProvider:
    def __init__(self, vobj):
        vobj.Proxy = self
        self.vobj = vobj

    def attach(self, vobj):
        mode = 2
        vobj.setEditorMode("LineWidth", mode)
        vobj.setEditorMode("MarkerColor", mode)
        vobj.setEditorMode("NormalColor", mode)
        vobj.setEditorMode("DisplayMode", mode)
        vobj.setEditorMode("BoundingBox", mode)
        vobj.setEditorMode("Selectable", mode)
        vobj.setEditorMode("ShapeAppearance", mode)
        vobj.setEditorMode("Transparency", mode)
        vobj.setEditorMode("Visibility", mode)
        self.vobj = vobj

    def dumps(self):
        return None

    def loads(self, state):
        return None

    def getIcon(self):
        return ":/icons/CAM_ToolController.svg"

    def onChanged(self, vobj, prop):
        mode = 2
        vobj.setEditorMode("LineWidth", mode)
        vobj.setEditorMode("MarkerColor", mode)
        vobj.setEditorMode("NormalColor", mode)
        vobj.setEditorMode("DisplayMode", mode)
        vobj.setEditorMode("BoundingBox", mode)
        vobj.setEditorMode("Selectable", mode)

    def onDelete(self, vobj, args=None):
        # Assuming PathUtil is imported or available
        # PathUtil.clearExpressionEngine(vobj.Object)
        # Check if Proxy exists before calling onDelete
        if hasattr(self.vobj.Object, 'Proxy') and hasattr(self.vobj.Object.Proxy, 'onDelete'):
             self.vobj.Object.Proxy.onDelete(vobj.Object, args)
        return True

    def updateData(self, vobj, prop):
        # this is executed when a property of the APP OBJECT changes
        pass

    def setupContextMenu(self, vobj, menu):
        # Assuming Path.Log is available if needed
        # Path.Log.track()
        for action in menu.actions():
            menu.removeAction(action)
        action = QtGui.QAction(translate("CAM", "Edit"), menu)
        action.triggered.connect(self._editInContextMenuTriggered)
        menu.addAction(action)

    def _editInContextMenuTriggered(self, checked):
        # Calls the potentially problematic setEdit
        # self.setEdit()
        # Maybe open the dialog directly instead?
        dlg = DlgToolControllerEdit(self.vobj.Object)
        dlg.exec_()


    def claimChildren(self):
        obj = self.vobj.Object
        # Ensure Tool property exists before accessing
        if obj and hasattr(obj, 'Proxy') and hasattr(obj, 'Tool') and obj.Tool:
            return [obj.Tool]
        return []

class ToolControllerEditor(object):
    def __init__(self, obj, asDialog):
        # IMPORTANT: This relies on DlgToolControllerEdit.ui being compiled
        # into the Qt resource system (e.g., via CMake).
        self.form = FreeCADGui.PySideUic.loadUi(":/panels/DlgToolControllerEdit.ui")
        if not asDialog:
            self.form.buttonBox.hide()
        self.obj = obj

        comboToPropertyMap = [("spindleDirection", "SpindleDir")]
        # Assuming propertyEnumerations is still valid on the base controller
        enumTups = PathToolController.ToolController.propertyEnumerations(dataType="raw")

        PathGuiUtil.populateCombobox(self.form, enumTups, comboToPropertyMap)
        self.vertFeed = PathGuiUtil.QuantitySpinBox(self.form.vertFeed, obj, "VertFeed")
        self.horizFeed = PathGuiUtil.QuantitySpinBox(self.form.horizFeed, obj, "HorizFeed")
        self.vertRapid = PathGuiUtil.QuantitySpinBox(self.form.vertRapid, obj, "VertRapid")
        self.horizRapid = PathGuiUtil.QuantitySpinBox(self.form.horizRapid, obj, "HorizRapid")

        # Hide the second page of the toolbox if it existed in the UI
        if self.form.toolBox.count() > 1:
             self.form.toolBox.widget(1).hide()
             self.form.toolBox.removeItem(1)

    def selectInComboBox(self, name, combo):
        """selectInComboBox(name, combo) ...
        helper function to select a specific value in a combo box."""
        blocker = QtCore.QSignalBlocker(combo)
        index = combo.currentIndex()  # Save initial index

        # Search using currentData and return if found
        newindex = combo.findData(name)
        if newindex >= 0:
            combo.setCurrentIndex(newindex)
            return

        # if not found, search using current text
        newindex = combo.findText(name, QtCore.Qt.MatchFixedString)
        if newindex >= 0:
            combo.setCurrentIndex(newindex)
            return

        # not found, return unchanged
        combo.setCurrentIndex(index)
        return

    def updateUi(self):
        tc = self.obj
        self.form.tcName.setText(tc.Label)
        self.form.tcNumber.setValue(tc.ToolNumber)
        self.horizFeed.updateSpinBox()
        self.horizRapid.updateSpinBox()
        self.vertFeed.updateSpinBox()
        self.vertRapid.updateSpinBox()
        self.form.spindleSpeed.setValue(tc.SpindleSpeed)

        self.selectInComboBox(tc.SpindleDir, self.form.spindleDirection)

    def updateToolController(self):
        tc = self.obj
        try:
            tc.Label = self.form.tcName.text()
            tc.ToolNumber = self.form.tcNumber.value()
            self.horizFeed.updateProperty()
            self.vertFeed.updateProperty()
            self.horizRapid.updateProperty()
            self.vertRapid.updateProperty()
            tc.SpindleSpeed = self.form.spindleSpeed.value()
            tc.SpindleDir = self.form.spindleDirection.currentData()


        except Exception as e:
            Path.Log.error("Error updating TC: {}".format(e))

    def refresh(self):
        self.form.blockSignals(True)
        self.updateToolController()
        self.updateUi()
        self.form.blockSignals(False)

    def setupUi(self):
        self.form.tcName.editingFinished.connect(self.refresh)
        self.form.horizFeed.editingFinished.connect(self.refresh)
        self.form.vertFeed.editingFinished.connect(self.refresh)
        self.form.horizRapid.editingFinished.connect(self.refresh)
        self.form.vertRapid.editingFinished.connect(self.refresh)
        self.form.spindleSpeed.editingFinished.connect(self.refresh)
        self.form.spindleDirection.currentIndexChanged.connect(self.refresh)


class DlgToolControllerEdit:
    def __init__(self, obj):
        self.editor = ToolControllerEditor(obj, True)
        self.editor.updateUi()
        self.editor.setupUi()
        self.obj = obj

    def exec_(self):
        restoreTC = self.obj.Proxy.templateAttrs(self.obj)

        rc = False
        if not self.editor.form.exec_():
            Path.Log.info("revert")
            self.obj.Proxy.setFromTemplate(self.obj, restoreTC)
            rc = True
        else:
            # Apply changes if OK was clicked
            self.editor.updateToolController()
            rc = True
        return rc

FreeCAD.Console.PrintLog("Loading Path.Tool.Gui.Controller... done\n")