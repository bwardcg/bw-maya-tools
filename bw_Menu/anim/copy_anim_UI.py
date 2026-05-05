"""
attempting to make a rig agnostic copy tool

usage:
    from bw_tools import bw_copyanim

    launch GUI:
        copyUI = bw_copyanim.CopyAnimUI()
        copyUI.show()
    run by command:
        bw_copyanim.copyKeys()
"""

import maya.cmds as cmds
from PySide6 import QtWidgets
from bw_tools.bw_ui_maya import MayaWindowBase


class CopyAnimUI(MayaWindowBase):
    def __init__(self):
        super().__init__(title='bw_copy', width=300, height=400)

        self.create_copy_controls()
        self.create_paste_options()
        self.create_frame_range()
        self.create_buttons()
        self.connnectSignals()

    def create_copy_controls(self):
        group = QtWidgets.QGroupBox('Copy Animation')
        vbox = QtWidgets.QVBoxLayout()

        self.r1 = QtWidgets.QRadioButton('All Source Controls')
        self.r2 = QtWidgets.QRadioButton('Body Only')
        self.r3 = QtWidgets.QRadioButton('Face Only')
        self.r4 = QtWidgets.QRadioButton('Selected Source Controls Only')
        self.r4.setChecked(True)

        for r in [self.r1, self.r2, self.r3, self.r4]:
            vbox.addWidget(r)

        group.setLayout(vbox)
        self.layout.addWidget(group)

    def create_paste_options(self):
        group = QtWidgets.QGroupBox('Paste Options')
        vbox = QtWidgets.QVBoxLayout()

        self.pOptions = []
        for option in ['replaceCompletely', 'replace', 'insert', 'merge']:
            radio = QtWidgets.QRadioButton(option)
            self.pOptions.append(radio)
            vbox.addWidget(radio)

        self.pOptions[0].setChecked(True)

        group.setLayout(vbox)
        self.layout.addWidget(group)

    def create_frame_range(self):
        group = QtWidgets.QGroupBox('Frame Range')
        vbox = QtWidgets.QVBoxLayout()

        self.f1 = QtWidgets.QRadioButton('All')
        self.f2 = QtWidgets.QRadioButton('Current Frame')
        self.f3 = QtWidgets.QRadioButton('Range')
        self.f1.setChecked(True)

        for f in [self.f1, self.f2, self.f3]:
            vbox.addWidget(f)

        hbox = QtWidgets.QHBoxLayout()
        startLabel = QtWidgets.QLabel('start:')
        self.start = QtWidgets.QLineEdit(str(cmds.playbackOptions(min=True, q=True)))
        endLabel = QtWidgets.QLabel('end:')
        self.end = QtWidgets.QLineEdit(str(cmds.playbackOptions(max=True, q=True)))

        for widget in [self.start, self.end]:
            widget.setFixedWidth(50)
            widget.setDisabled(True)

        startLabel.setFixedWidth(25)
        endLabel.setFixedWidth(25)

        hbox.addWidget(startLabel)
        hbox.addWidget(self.start)
        hbox.addStretch()
        hbox.addWidget(endLabel)
        hbox.addWidget(self.end)

        vbox.addLayout(hbox)
        group.setLayout(vbox)
        self.layout.addWidget(group)

    def create_buttons(self):
        hbox = QtWidgets.QHBoxLayout()
        self.applyButton = QtWidgets.QPushButton('Apply')
        self.closeButton = QtWidgets.QPushButton('Close')
        hbox.addWidget(self.applyButton)
        hbox.addWidget(self.closeButton)
        self.layout.addLayout(hbox)

    def connnectSignals(self):
        self.applyButton.clicked.connect(self.applyCb)
        self.closeButton.clicked.connect(self.close)
        self.f1.clicked.connect(self.frameRangeCb)
        self.f2.clicked.connect(self.frameRangeCb)
        self.f3.clicked.connect(self.frameRangeCb)

    def frameRangeCb(self):
        """
        Enables or disables the frame range elements
        """
        if self.f3.isChecked():
            self.start.setEnabled(True)
            self.end.setEnabled(True)
        else:
            self.start.setDisabled(True)
            self.end.setDisabled(True)

    def getSourceSelection(self):
        if self.r1.isChecked():
            return 'All'
        if self.r2.isChecked():
            return 'Body'
        if self.r3.isChecked():
            return 'Face'
        if self.r4.isChecked():
            return 'Selected'
        else:
            return False

    def getPasteOption(self):
        for option in self.pOptions:
            if option.isChecked():
                return str(option.text())

    def applyCb(self):
        time = []
        if self.f3.isChecked():
            try:
                start = int(self.start.text())
                end = int(self.end.text())
                time = [start, end]
            except Exception as e:
                cmds.warning('Need to specify a valid frame range: ' + e.message)
                return
        elif self.f2.isChecked():
            now = cmds.currentTime(query=True)
            time = [now, now]

        # target is last selection
        target = getSelected(return_target=True)
        if target:
            ctrls = getCtrls(method=self.getSourceSelection())
            copyKeys(target, ctrls, pasteOption=self.getPasteOption(), time=time)


def getCtrls(method):
    """
    attempt to get list of controls for given rig
    presumably a method is being imported and added for whatever rig is used
    """
    ctrls = []

    if method == 'All':
        # get ALL ctrls (for whatever rig you're using)
        cmds.warning("getCtrls method {} not currently supported".format(method))

    elif method == 'Body':
        # get Body ctrls (for whatever rig you're using)
        cmds.warning("getCtrls method {} not currently supported".format(method))

    elif method == 'Face':
        # get Face ctrls (for whatever rig you're using)
        cmds.warning("getCtrls method {} not currently supported".format(method))

    elif method == 'Selected':
        # get Selected ctrls
        for s in getSelected():
            if cmds.objectType(s, isAType='transform'):
                ctrls.append(s)

    else:
        cmds.warning('could not determine selection method')

    return ctrls


def getSelected(return_target=False):
    """
    Uses selected for Source Ctrls
    Last obj in selection will be the target
    """
    selected = cmds.ls(sl=True)
    if len(selected) > 1:
        target = selected.pop(-1)
        if return_target:
            return target
        else:
            return selected
    else:
        cmds.warning("please select at least 2 transforms before running")
        return False


def testInput(target, source):

    # test source(s) namespace
    if source:
        if len(source[0].split(":")) > 0:
            testNS = set()
            for s in source:
                testNS.add(s.split(":")[0])
            if len(testNS) == 1:
                sourceNS = list(testNS)[0]
                print('Source namespace verified: {}'.format(sourceNS))
            else:
                cmds.warning('!!! source objs must be in same namespace! or results may be unexpected.')
                sourceNS = None
        else:
            sourceNS = None
    else:
        sourceNS = None
        cmds.warning('*** SOURCE CTRLS NOT FOUND!')

    # test target namespace
    if target:
        if len(target.split(":")) > 1:
            targetNS = target.split(":")[0]
            if not targetNS == sourceNS:
                print('Target namespace verified: {}'.format(targetNS))
                return targetNS, sourceNS
            else:
                cmds.warning('*** target obj must NOT be in SOURCE namespace!')
        else:
            cmds.warning('*** target obj must be in a namespace!')
    else:
        cmds.warning('*** TARGET CTRL NOT FOUND!')

    return None, None


def copyKeys(target=None, ctrls=None, pasteOption='replaceCompletely', time=[]):
    """
    Copies the keys from one character to another
    :Parameters:
        target: `str`
            Ctrl from the target rig (MUST BE IN NAMESPACE)
        ctrls: `list of strings`
            list of SOURCE Ctrls (NOT IN TARGET NAMESPACE)
        pasteOptions: `str`
            options to pass to pasteKey.  Valid values are "insert", "replace", "replaceCompletely",
            "merge", "scaleInsert," "scaleReplace", "scaleMerge", "fitInsert", "fitReplace", and "fitMerge".
            The default paste option is: 'replaceCompletely'.
        time: `list`
            A list of integers representing the in/out for the frameRange
    """

    if target is None and ctrls is None:
        print("operating on SELECTION")
        ctrls = getSelected()
        target = getSelected(return_target=True)
        print("ctrls: {}".format(ctrls))

    # test that namespaces make sense
    targetNS, sourceNS = testInput(target, ctrls)

    if targetNS:
        print('bw_copyAnim copying to {} namespace from : {}'.format(targetNS, ctrls))
        # loop the SOURCE ctrls and look for each Ctrl in Target NameSpace
        for ctrl in ctrls:
            # use last token in namespaces for ctrl name
            ctrlName = ctrl.split(":")[-1]
            targetCtrl = '{}:{}'.format(targetNS, ctrlName)

            if cmds.objExists(targetCtrl):
                # copy the curves from source ctrl
                if time:
                    copySuccess = cmds.copyKey(str(ctrl), option="curve", time=(time[0], time[1]))
                else:
                    copySuccess = cmds.copyKey(str(ctrl), option="curve")

                if copySuccess:
                    print('Copying keys for: {}'.format(ctrlName))

                    # paste curves to target ctrl
                    try:
                        cmds.pasteKey(targetCtrl, option=pasteOption)
                    except Exception as e:
                        cmds.warning('Error pasting keys for {} : {}'.format(targetCtrl, e.message))
                        continue
                    # Set matching attributes
                    for attr in cmds.listAttr(ctrl, keyable=True, unlocked=True):
                        if cmds.attributeQuery(attr, node=ctrl, exists=True):
                            try:
                                val = cmds.getAttr('{}.{}'.format(ctrl, attr))
                                cmds.setAttr('{}.{}'.format(targetCtrl, attr), val)
                            except Exception as e:
                                cmds.warning('Error copying attr for {} : {}'.format(targetCtrl, e))
                                continue
                        else:
                            cmds.warning('Attr not found: {}.{}'.format(targetCtrl, attr))
                else:
                    cmds.warning('no curves copied from: {}'.format(ctrl))
            else:
                cmds.warning('Ctrl not found: {}'.format(targetCtrl))
    else:
        cmds.warning('bw_copyAnim requires a list of source ctrls and a target rig ctrl in a namespace')


# ------------------------------- run with bw_Menu
def run():
    CopyAnimUI.launch()