import maya.cmds as cmds
from bw_tools.rigging import bw_rigUtils


class Rivet(object):
    """
    constrain a locator to a skeleton to match a vertex position from skin weight
    # todo: currently only works on single vertex
    """

    def __init__(self, vertex=None, interp="shortest", threshold=.01):
        """
        declare some variables
        """
        self.vert = vertex
        self.interp = interp
        self.weightThreshold = threshold
        self.influences = []
        self.weights = []
        self.obj = None
        self.null = None

    def getVertexWeights(self, vert):
        """
        get skin weight values from vert
        :param vert: flat vertex name
        :return: list of influences, list of weights
        """
        skin = bw_rigUtils.getSkinCluster(self.obj)
        self.influences = cmds.skinPercent( skin, vert, ignoreBelow= self.weightThreshold, query=True, transform=None)
        self.weights = cmds.skinPercent( skin, vert, ignoreBelow= self.weightThreshold, query=True , value=True )
        if len(self.influences) == len(self.weights):
            return self.influences,self.weights
        else:
            cmds.warning("unequal number of influences and weights!!")

    def getObject(self):
        """
        check integrity for obj and it's vertex
        """
        # test user input vertex
        if self.isVertex(self.vert):
            self.obj = self.vert.split(".")[0]
            if cmds.objExists(self.obj):
                return True

        # fall back to selection
        for sel in cmds.ls(sl=1, fl=True):
            if self.isVertex(sel):
                print("found vertex in selection: {}".format(sel))
                self.vert = sel
                self.obj = self.vert.split(".")[0]
                return True

        cmds.warning("please select a vert before running")
        return False

    def isVertex(self, testObj):
        """
        check if I've got a real vertex
        """
        # check first 3 chars of last token
        tokens = testObj.split(".")
        if tokens[-1][:3] == 'vtx':
            return True
        else:
            cmds.warning("input is not vertex: {}".format(testObj))
            return False

    def constrNullToVert(self):
        """
        constrain null to vert with skin weight values
        """
        # verify vert and obj vars
        if self.getObject():
            # create null
            self.null = cmds.group(em=True, name=self.obj + "_followSkin_GRP#")

            # snap to vert pos
            vertPos = cmds.xform(self.vert, q=True, ws=True, t=True)
            cmds.move(vertPos[0], vertPos[1], vertPos[2], self.null)

            # constrain null to skin influences
            self.getVertexWeights(self.vert)
            for i in range(len(self.influences)):
                inf = self.influences[i]
                weight = round(self.weights[i], 2)
                print("constraining {} to {} at {} weight".format(self.null, inf, weight))
                constr = cmds.parentConstraint(inf, self.null, w=weight, mo=True, n="cstr_" + self.obj + "#")

            # set constraint interpolation type to "shortest"
            cmds.setAttr(str(constr[0]) + ".interpType", 2)

            # toggle selection type back to object
            cmds.SelectToggleMode()
