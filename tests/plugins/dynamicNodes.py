"""Simple Python plugin used by the OpenMayaHelper plugin tests."""

import maya.OpenMaya as om
import maya.OpenMayaMPx as ommpx


NODE_NAME = "initialNode"
NODE_ID = om.MTypeId(0x0013A201)


class InitialNode(ommpx.MPxNode):
    aFloat = om.MObject()

    @staticmethod
    def creator():
        return ommpx.asMPxPtr(InitialNode())

    @staticmethod
    def initialize():
        numeric_attr = om.MFnNumericAttribute()
        InitialNode.aFloat = numeric_attr.create("aFloat", "af", om.MFnNumericData.kFloat, 0.0)
        numeric_attr.setKeyable(True)
        InitialNode.addAttribute(InitialNode.aFloat)


def initializePlugin(mobject):
    plugin = ommpx.MFnPlugin(mobject, "OpenMayaHelper", "0.1.0", "Any")
    plugin.registerNode(NODE_NAME, NODE_ID, InitialNode.creator, InitialNode.initialize)


def uninitializePlugin(mobject):
    plugin = ommpx.MFnPlugin(mobject)
    plugin.deregisterNode(NODE_ID)
