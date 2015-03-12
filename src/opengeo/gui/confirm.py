'''
Routines to ask for confirmation when performing certain operations 
'''
from PyQt4 import QtGui, QtCore

def _confirmationBox(title, msg):
    QtGui.QApplication.restoreOverrideCursor()
    ret = QtGui.QMessageBox.warning(None, title, msg,
                                    QtGui.QMessageBox.Yes |
                                    QtGui.QMessageBox.No,
                                    QtGui.QMessageBox.No)
    QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
    return ret == QtGui.QMessageBox.Yes


def confirmDelete():
    askConfirmation = bool(QtCore.QSettings().value("/OpenGeo/Settings/General/ConfirmDelete", True, bool))
    if not askConfirmation:
        return True
    msg = "You confirm that you want to delete the selected elements?"
    reply = QtGui.QMessageBox.question(None, "Delete confirmation",
                                       msg, QtGui.QMessageBox.Yes |
                                       QtGui.QMessageBox.No,
                                       QtGui.QMessageBox.No)
    return reply != QtGui.QMessageBox.No


# noinspection PyPep8Naming
class DeleteDependentsDialog(QtGui.QDialog):

    def __init__(self, dependent, parent=None):
        super(DeleteDependentsDialog, self).__init__(parent)
        self.title = "Confirm Deletion"
        self.msg = "The following elements depend on the elements to delete " \
                   "and will be deleted as well:"
        typeorder = ['LayerGroup', 'Layer', 'GwcLayer', 'Other']
        names = dict()
        for dep in dependent:
            cls = dep.__class__.__name__
            name = dep.name
            title = ''
            if hasattr(dep, 'resource'):
                if hasattr(dep.resource, 'title'):
                    if dep.resource.title != name:
                        title = dep.resource.title
            desc = "<b>- {0}:</b> &nbsp;{1}{2}".format(
                cls,
                name,
                " ({0})".format(title) if title else ''
            )
            if cls in names:
                names[cls].append(desc)
            else:
                if cls in typeorder:
                    names[cls] = [desc]
                else:
                    if 'Other' in names:
                        names['Other'].append(desc)
                    else:
                        names['Other'] = [desc]

        self.deletes = "<br><br>".join(
            ["<br><br>".join(sorted(list(set(names[typ]))))
             for typ in typeorder if typ in names])
        self.question = "Do you really want to delete all these elements?"
        self.buttonBox = None
        self.initGui()

    def initGui(self):
        self.setWindowTitle(self.title)
        layout = QtGui.QVBoxLayout()

        msgLabel = QtGui.QLabel(self.msg)
        msgLabel.setWordWrap(True)
        layout.addWidget(msgLabel)

        deletesView = QtGui.QTextEdit()
        deletesView.setText(unicode(self.deletes))
        deletesView.setReadOnly(True)
        deletesView.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        layout.addWidget(deletesView)

        questLabel = QtGui.QLabel(self.question)
        questLabel.setWordWrap(True)
        questLabel.setAlignment(QtCore.Qt.AlignHCenter)
        layout.addWidget(questLabel)

        self.buttonBox = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)
        # noinspection PyUnresolvedReferences
        self.buttonBox.accepted.connect(self.accept)
        # noinspection PyUnresolvedReferences
        self.buttonBox.rejected.connect(self.reject)

        self.setMinimumWidth(400)
        self.setMinimumHeight(400)
        self.resize(500, 400)
