# -*- coding: utf-8 -*-

##\namespace profesor
from xdg import DesktopEntry
from xdg import IconTheme

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from sigala.common.exception import DesktopFileNotFound
from sigala.profesor.settings import DEFAULT_APP_ICON

# Class that creates a QMenuItem from a .desktop file
##\class SAppLauncher
#\brief A custom QAction that gets its behavior from a .desktop file.
class SAppLauncher(QAction):
    # Clase que hereda de QAction. Obtiene como parámetro un fichero .desktop
    # y crea la entrada de menú correspondiente.

    ## \fn __init__(self, desktop_file, parent)
    # \brief Creates a new SAppLauncher from a desktop file
    # \param desktop_file .desktop file to read data from.
    # \param parent The parent of the action
    def __init__(self, desktop_file, parent=None):
        super(SAppLauncher, self).__init__(parent)
        self._createAppLauncher(desktop_file)

    ##\fn _createAppLauncher(self, df)
    #\brief Populates the QAppLauncher instance.
    #\param df Desktop file name.
    def _createAppLauncher(self, df):
        try:
            entry = DesktopEntry.DesktopEntry(filename=df)
        except UnboundLocalError, m:
            raise DesktopFileNotFound("Nonexistent .desktop file: '%s'" % df)

        app_icon_name = entry.getIcon()
        app_comment = entry.getComment()
        app_title = entry.getName()

        self.app_exec = entry.getExec()

        app_icon = self._getQIcon(app_icon_name)

        self.setToolTip(app_comment)
        self.setText(app_title)
        self.setIcon(app_icon)

    ##\fn _getQIcon(self, icon_name)
    #\brief Returns the path for the named icon or 
    # a default icon path if not found.
    #\param icon_name The name of the icon to search for.
    def _getQIcon(self, icon_name):
        # Returns a QICon object from the icon name.
        icon_path = IconTheme.getIconPath(icon_name)
        if icon_path is None:
            icon_path = DEFAULT_APP_ICON
        return QIcon(icon_path)

    ##\fn ExecCommand(self)
    #\brief Returns the command to be executed.
    def ExecCommand(self):
        return self.app_exec

    def __unicode__(self):
        return u"%s - %s" % (self.text(), self.toolTip())

    def __repr__(self):
        return unicode(self)

class TestClass(QMainWindow):
    def __init__(self, parent=None):
        super(TestClass, self).__init__(parent)
        boton = QPushButton("No pulsar, No hace nada.")
        self.a = SAppLauncher("/usr/share/applications/blender-fullscreen.desktop")
        self.connect(self.a, SIGNAL("triggered()"), 
                    lambda: self.action_clicked(self.a.ExecCommand()))
        self.setCentralWidget(boton)
        self.setup_menu()

    def setup_menu(self):
        mb = self.menuBar()
        m_acciones = mb.addMenu("Acciones")
        m_acciones.addAction(self.a)
        mb.show()


    def action_clicked(self, c):
        print "Ejecutando" , c


if __name__=="__main__":
    import sys
    app = QApplication(sys.argv)
    t = TestClass()
    t.show()
    app.exec_()

