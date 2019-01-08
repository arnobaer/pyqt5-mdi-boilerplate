from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

import argparse
import sys, os

__version__ = "1.0.0"

# -----------------------------------------------------------------------------
#  Main window class.
# -----------------------------------------------------------------------------

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.AppTitle = self.tr("MDI Boilerplate")
        self.AppVersion = __version__

        # Setup main window.
        self.setWindowTitle(self.AppTitle)
        self.setWindowIcon(QtGui.QIcon.fromTheme('utilities-system-monitor'))
        self.resize(800, 600)

        # Create menus, toolbars and status bar.
        self.createActions()
        self.createToolbars()
        self.createMenubar()
        self.createStatusbar()

        # Setup central MDI area.
        self.mdiArea = MdiArea(self)
        self.setCentralWidget(self.mdiArea)

        # Setup timed watchdog.
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.onWatchdogEvent)
        timer.start(1000)

    def createActions(self):
        """Create actions used in menu bar and tool bars."""

        # Action for opening a new connections file.
        self.openAct = QtWidgets.QAction(self.tr("&Open..."), self)
        self.openAct.setShortcut(QtGui.QKeySequence.Open)
        self.openAct.setStatusTip(self.tr("Open an existing file"))
        self.openAct.setIcon(QtGui.QIcon.fromTheme('document-open'))
        self.openAct.triggered.connect(self.onOpen)

        self.closeAct = QtWidgets.QAction(self.tr("&Close"), self)
        self.closeAct.setShortcuts(QtGui.QKeySequence.Close)
        self.closeAct.setStatusTip(self.tr("Close the current file"))
        self.closeAct.setEnabled(False)
        self.closeAct.triggered.connect(self.onClose)

        # Action to quit the application.
        self.quitAct = QtWidgets.QAction(self.tr("&Quit"), self)
        self.quitAct.setShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Q))
        self.quitAct.setStatusTip(self.tr("Exit"))
        self.quitAct.triggered.connect(self.onQuit)

        # Action for refreshing readable items.
        self.refreshAct = QtWidgets.QAction(self.tr("&Refresh"), self)
        self.refreshAct.setShortcut(QtGui.QKeySequence.Refresh)
        self.refreshAct.setStatusTip(self.tr("Refresh by reading data from file"))
        self.refreshAct.setIcon(QtGui.QIcon.fromTheme('view-refresh'))
        self.refreshAct.setEnabled(False)
        self.refreshAct.triggered.connect(self.onRefresh)

        # Action for toggling status bar.
        self.statusbarAct = QtWidgets.QAction(self.tr("&Statusbar"), self)
        self.statusbarAct.setCheckable(True)
        self.statusbarAct.setChecked(True)
        self.statusbarAct.setStatusTip(self.tr("Show or hide the statusbar in the current window"))
        self.statusbarAct.toggled.connect(self.onToggleStatusBar)

        # Actions to show online contents help.
        self.contentsAct = QtWidgets.QAction(self.tr("&Contents"), self)
        self.contentsAct.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F1))
        self.contentsAct.triggered.connect(self.onContents)

        # Actions to show about dialog.
        self.aboutAct = QtWidgets.QAction(self.tr("&About"), self)
        self.aboutAct.triggered.connect(self.onAbout)

    def createToolbars(self):
        """Create tool bars and setup their behaviors (floating or static)."""

        self.toolbar = self.addToolBar(self.tr("Toolbar"))
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.toolbar.addAction(self.openAct)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.refreshAct)

        # Create action for toggling the tool bar here.
        self.toolbarAct = self.toolbar.toggleViewAction() # Get predefined action from toolbar.
        self.toolbarAct.setStatusTip(self.tr("Show or hide the toolbar in the current window"))

    def createMenubar(self):
        """Create menu bar with entries."""

        # Menu entry for file actions.
        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.closeAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAct)

        # Menu entry for view actions.
        self.viewMenu = self.menuBar().addMenu(self.tr("&View"))
        self.viewMenu.addAction(self.refreshAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.toolbar.toggleViewAction())
        self.viewMenu.addAction(self.statusbarAct)

        # Menu entry for help actions.
        self.helpMenu = self.menuBar().addMenu(self.tr("&Help"))
        self.helpMenu.addAction(self.contentsAct)
        self.helpMenu.addSeparator()
        self.helpMenu.addAction(self.aboutAct)

    def createStatusbar(self):
        """Create status bar and content."""
        self.statusBar()
        self.statusBar().showMessage(self.tr("Ready."))

    def onOpen(self):
        """Select a file using a file open dialog."""
        filename, filetype = QtWidgets.QFileDialog.getOpenFileName(self,
            self.tr("Open file"),
            os.getcwd(),
            self.tr("All files (*)")
        )
        # Return if user did not select a file.
        if not filename:
            return
        self.loadDocument(filename)

    def onClose(self):
        self.mdiArea.closeDocument()
        self.closeAct.setEnabled(self.mdiArea.count())

    def onQuit(self):
        self.close()

    def onRefresh(self, checked):
        document = self.mdiArea.currentDocument()
        if document:
            index = self.mdiArea.indexOf(document)
            label = os.path.basename(document.filename)
            self.mdiArea.setTabText(index, label)
            document.reload()

    def onToggleStatusBar(self):
        """Toggles the visibility of the status bar."""
        self.statusBar().setVisible(self.statusbarAct.isChecked())

    def onContents(self):
        QtWidgets.QMessageBox.information(self, self.tr("Contents"), self.tr("<p>Please refer to...</p>"))

    def onAbout(self):
        QtWidgets.QMessageBox.information(self, self.tr("About"),
             self.tr("<p><strong>{}</strong></p>"
            "<p>Version {}</p>"
            "<p>Authors: ...</p>").format(self.AppTitle, self.AppVersion)
        )

    def onWatchdogEvent(self):
        """Perform checks in regular intervals."""
        self.mdiArea.checkTimestamps()

    def loadDocument(self, filename):
        """Load document from filename."""
        filename = os.path.abspath(filename)
        if not os.path.isfile(filename):
            raise NoSuchFileError(filename)
        # Do not open files twice, just reload them.
        for index in range(self.mdiArea.count()):
            document = self.mdiArea.widget(index)
            if document:
                if filename == document.filename:
                    self.mdiArea.setCurrentIndex(index)
                    document.reload()
                    return
        # Else load from file and create new document tab.
        self.statusBar().showMessage(self.tr("Loading..."), 2500)
        document = Document(filename, self)
        index = self.mdiArea.addDocument(document)
        self.mdiArea.setCurrentIndex(index)

        # After loading a conenction file, it is possible to refresh the current module.
        self.refreshAct.setEnabled(True)
        self.statusBar().showMessage(self.tr("Successfully loaded file"), 2500)

        # Enable close action
        self.closeAct.setEnabled(self.mdiArea.count())

# -----------------------------------------------------------------------------
#  MDI Area class.
# -----------------------------------------------------------------------------

class MdiArea(QtWidgets.QTabWidget):

    def __init__(self, parent=None):
        super(MdiArea, self).__init__(parent)
        self.setDocumentMode(True)
        self.setTabsClosable(True)
        self.setMovable(True)

        # Close document by clicking on the tab close button.
        self.tabCloseRequested.connect(self.closeDocument)

    def addDocument(self, document):
        document.fileChanged.connect(self.onFileChanged)
        document.fileLoaded.connect(self.onFileLoaded)
        return self.addTab(document, QtGui.QIcon.fromTheme('ascii'), os.path.basename(document.filename))

    def currentDocument(self):
        """Return current active document."""
        return self.widget(self.currentIndex())

    def documents(self):
        """Returns iterator of all documents."""
        for index in range(self.count()):
            yield self.widget(index)

    def closeDocument(self):
        """Close current active document. Provided for convenience.
        """
        index = self.currentIndex()
        # Finally remove tab by index.
        self.removeTab(index)

    def setDocumentChanged(self, document, changed):
        index = self.indexOf(document)
        label = os.path.basename(document.filename)
        self.setTabText(index, "{}{}".format('*' if changed else '', label))

    def checkTimestamps(self):
        for document in self.documents():
            document.checkTimestamp()

    def onFileLoaded(self, document):
        self.setDocumentChanged(document, False)

    def onFileChanged(self, document):
        self.setDocumentChanged(document, True)


# -----------------------------------------------------------------------------
#  Document class.
# -----------------------------------------------------------------------------

class Document(QtWidgets.QWidget):
    """Generic document widget."""

    fileLoaded = QtCore.pyqtSignal(QtWidgets.QWidget)
    fileChanged = QtCore.pyqtSignal(QtWidgets.QWidget)

    def __init__(self, filename, parent=None):
        super(Document, self).__init__(parent)
        self.filename = os.path.abspath(filename)
        self.textEdit = self.createTextEdit()
        self.warningLabel = self.createWarningLabel()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.warningLabel)
        layout.addWidget(self.textEdit)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        # Load the file.
        QtCore.QCoreApplication.instance().processEvents()
        self.reload()

    def createTextEdit(self):
        """Create text editor."""
        textEdit = QtWidgets.QTextEdit(self)
        # Disable editing.
        textEdit.setReadOnly(True)
        # Set a monospace font for content.
        textEdit.setFont(QtGui.QFont("Monospace", 10))
        return textEdit

    def createWarningLabel(self):
        label = QtWidgets.QLabel(self)
        label.setObjectName("warningLabel")
        label.setStyleSheet(
            "padding: 16px;"
            "background-color: #f9ac3a;"
            "border: none;"
        )
        label.setWordWrap(True)
        label.hide()
        return label

    def reload(self):
        """Reload from file."""
        with open(self.filename) as f:
            self.timestamp = os.path.getmtime(self.filename)
            self.textEdit.setText(f.read())
            self.fileLoaded.emit(self)
        self.clearWarning()

    def clearWarning(self):
        """Clear the warning badge located at the top of the document."""
        self.warningLabel.clear()
        self.warningLabel.hide()

    def showWarning(self, message):
        """Show a warning badge displaying a message located at the top of the document."""
        self.warningLabel.setText(message)
        self.warningLabel.show()

    def checkTimestamp(self):
        timestamp = os.path.getmtime(self.filename)
        if timestamp > self.timestamp:
            self.showWarning(self.tr("<strong>The file {} changed on disk.</strong> Reload (hit Ctrl+R) to see the changes.").format(self.filename))
            self.fileChanged.emit(self)
        else:
            self.clearWarning()

# -----------------------------------------------------------------------------
#  Parsing command line arguments
# -----------------------------------------------------------------------------

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(prog=os.path.basename(__file__), description="")
    parser.add_argument('filename', nargs="*", metavar='<file>', help="file")
    parser.add_argument('-V, --version', action='version', version='%(prog)s {}'.format(__version__))
    return parser.parse_args()

# -----------------------------------------------------------------------------
#  Main routine
# -----------------------------------------------------------------------------

def main():
    """Main routine."""
    args = parse_args()

    # Create application and main window.
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # Open connections file using command line argument.
    for filename in args.filename:
        window.loadDocument(filename)

    # Run execution loop.
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())
