"""
State:          PolypenV2
State type:     polypenV2
Description:    PolypenV2
Author:         justi
Date Created:   February 13, 2025 - 01:05:41
"""


import hou
import viewerstate.utils as su
import json

COLOR_H = hou.Color(0,1,1)
COLOR_S = hou.Color(1,1,0)
SIZE2 = 3
SIZE7 = 7

class State(object):
    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.scene_viewer = scene_viewer

        self.gi = None
        self.geometry = None
        self.xform_handle = hou.Handle(self.scene_viewer, "Transform")
        self.transform_data = None
        
        # the transform node parms to map onto the handle
        self.parm_names = [
            "tx",
            "ty",
            "tz",
            "rx",
            "ry",
            "rz",
            "sx",
            "sy",
            "sz",
            "px",
            "py",
            "pz",
            "pivot_rx",
            "pivot_ry",
            "pivot_rz" ]

        # Geometry drawable
        self.mygeo = hou.GeometryDrawableGroup("drawableGeo")
        self.mygeo.addDrawable(hou.GeometryDrawable(self.scene_viewer, hou.drawableGeometryType.Point, "points_h", params={"color1":COLOR_H, "radius":SIZE7, "style":hou.drawableGeometryPointStyle.LinearCircle}))
        self.mygeo.addDrawable(hou.GeometryDrawable(self.scene_viewer, hou.drawableGeometryType.Point, "points_s", params={"color1":COLOR_S}))
        self.mygeo.addDrawable(hou.GeometryDrawable(self.scene_viewer, hou.drawableGeometryType.Point, "points_n", params={"color1":COLOR_S, "highlight_mode":hou.drawableHighlightMode.Transparent}))
        self.mygeo.addDrawable(hou.GeometryDrawable(self.scene_viewer, hou.drawableGeometryType.Face, "face_h", params={"color1":COLOR_H}))
        self.mygeo.addDrawable(hou.GeometryDrawable(self.scene_viewer, hou.drawableGeometryType.Face, "face_s", params={"color1":COLOR_S}))
        self.mygeo.addDrawable(hou.GeometryDrawable(self.scene_viewer, hou.drawableGeometryType.Face, "face_n", params={"color1":COLOR_S, "highlight_mode":hou.drawableHighlightMode.Transparent}))


        self.myedge = hou.GeometryDrawableGroup("drawableEdge")
        self.myedge.addDrawable(hou.GeometryDrawable(self.scene_viewer, hou.drawableGeometryType.Line, "line_h", params={"color1":COLOR_H, "line_width":SIZE2}))

        # support for rendering drawable
        self.prev_prim_num = -1
        self.prim_selection = None
        self.point_selection = None
        self.edge_selection = None

        self.selectionMode = None

    def buildEdge(self,edge):
        """ 
        Create line primitive
        """
        lineDrawable = hou.Geometry()

        P1 = lineDrawable.createPoint()
        P2 = lineDrawable.createPoint()
        
        # Set positions for points
        P1.setPosition(edge[0].position())
        P2.setPosition(edge[1].position())
        
        # Create a line primitive
        line = lineDrawable.createPolygon()
        line.addVertex(P1)
        line.addVertex(P2)
        
        return lineDrawable

    def alignVector(v1, v2):
        """ Aligns v1 to v2 and returns the resulting vector.
        """
        v1 = v1.normalized()
        v2 = v2.normalized()
        axis = v1.cross( v2 )

        cosA = v1.dot( v2 )
        k = 1.0 / (1.0 + cosA)

        x = axis.x()
        y = axis.y()
        z = axis.z()
        mat = hou.Matrix3( ((x * x * k) + cosA,
                     (y * x * k) - z, 
                     (z * x * k) + y,
                     (x * y * k) + z,  
                     (y * y * k) + cosA,      
                     (z * y * k) - x,
                     (x * z * k) - y,  
                     (y * z * k) + x,  
                     (z * z * k) + cosA) )

        return mat.inverted().extractRotates()

    
    def initTransform(self, node):
        for parm_name in self.parm_names:
            node.parm(parm_name).set(0)
        node.parm("group").set("")        
        node.parm("sx").set(1)
        node.parm("sy").set(1)
        node.parm("sz").set(1)

        #---------------------------------------------------------------------------
        #---------------------------------------------------------------------------


    def onEnter(self,kwargs):
        """ Called on node bound states when it starts
        """
        node = kwargs["node"]
        state_parms = kwargs["state_parms"]
        self.geometry = node.geometry()
        self.gi = su.GeometryIntersector(self.geometry, self.scene_viewer)
        self.mygeo.setGeometry(self.geometry)
        self.mygeo.drawable("points_n").show(True)
        self.mygeo.drawable("face_n").show(True)
        self.xform_handle.show(False)


    def onExit(self,kwargs):
        """ Called when the state terminates
        """
        state_parms = kwargs["state_parms"]

    
    
    def onDraw(self, kwargs):
        """ Called for rendering a state e.g. required for 
        hou.AdvancedDrawable objects
        """
        draw_handle = kwargs["draw_handle"]
        self.mygeo.draw(draw_handle)
        self.myedge.draw(draw_handle)

    def onBeginHandleToState(self, kwargs):
        """ Open an undo bracket for the handle operations.
        """
        self.scene_viewer.beginStateUndo("Geo Deformer Interaction")        

    def onEndHandleToState(self, kwargs):
        """ Close the handle undo bracket.
        """
        self.scene_viewer.endStateUndo()
        
    def onHandleToState(self, kwargs):
        """ Sets the node parms with the handle parms.
        """
        parms = kwargs["parms"]
        node = kwargs["node"]                
        for parm_name in self.parm_names:
            node.parm(parm_name).set(parms[parm_name])
        tx = node.parm("tx").eval()    
        ty = node.parm("tx").eval()    
        tz = node.parm("tx").eval()  
        t = hou.Vector3(tx, ty, tz)  
        if t == (0.0,0.0,0.0):
            node.parm("toggleAction").set(0)
        else:
            node.parm("toggleAction").set(1)
                                    
    def onStateToHandle(self, kwargs):
        """ Sets the handle parms with the node parms.
        """                       
        node = kwargs["node"]
        parms = kwargs["parms"]        
        for parm_name in self.parm_names:
            parms[parm_name] = node.parm(parm_name).eval()        
        self.xform_handle.show(True)

    def onSelection(self, kwargs):
        """ Called when a selector has selected something
        """        
        selection = kwargs["selection"]
        node = kwargs["node"]
        state_parms = kwargs["state_parms"]
        geo = self.geometry
        self.initTransform(node)
        
        

        if not selection or len(selection.selectionStrings()) == 0:
            return False

        if selection is not None:
            sel_type = selection.geometryType()
            sel_ids = selection
            sel_str = selection.selectionStrings()[0]
            geo = node.geometry()
            old_data_str = node.parm("transform_data").eval()
            
            
            if sel_type == hou.geometryType.Primitives:
                bbox = geo.primBoundingBox(sel_str)
                
            elif sel_type == hou.geometryType.Edges:
                edges = geo.globEdges(sel_str)  # Récupère un tuple de hou.Edge
                edgepoints = [point for edge in edges for point in edge.points()]
                
                # Récupérer l'index de chaque point
                pointid = [point.number() for point in edgepoints]
                point_ids_str = " ".join(map(str, pointid))
                bbox = geo.pointBoundingBox(point_ids_str)

            elif sel_type == hou.geometryType.Points:
                bbox = geo.pointBoundingBox(str(sel_ids))
                sel_points = geo.globPoints(str(sel_ids), ordered=False)
                
                sel_ids = [point.number() for point in sel_points]
                
            pivot_pos = bbox.center()

                       
            
            old_data = json.loads(old_data_str) if old_data_str else{}
            if "selections" not in old_data:
                old_data["selections"] = []

            selection_data = {
                "type": str(sel_type),  # Peut être "point", "edge" ou "face"
                "ids": {
                sel_ids: () for sel_ids in sel_ids

                },  # Liste des identifiants sélectionnés
            }

            old_data["selections"].append(selection_data)

            
            node.parm("px").set(pivot_pos[0])
            node.parm("py").set(pivot_pos[1])
            node.parm("pz").set(pivot_pos[2])
            node.parm("group").set(sel_str)
            node.parm("geometryType").set(str(sel_type))
            node.parm("transform_data").set(json.dumps(old_data))
            node.parm("toggleAction").set(0)
            self.xform_handle.show(True)
            self.xform_handle.update()
            
           
        
        # Must return True to accept the selection
        return False

def createViewerStateTemplate():
    """ Mandatory entry point to create and return the viewer state 
        template to register. """

    state_typename = "polypenV2"
    state_label = "PolypenV2"
    state_cat = hou.sopNodeTypeCategory()

    template = hou.ViewerStateTemplate(state_typename, state_label, state_cat)
    template.bindFactory(State)
    template.bindIcon("$HOME/houdini20.5/otls/Icon/polyPen4.png")

    hotkey_definitions = hou.PluginHotkeyDefinitions()
    hk1 = su.defineHotkey(hotkey_definitions,
                          state_typename, "drawable selector", "k")
    hk2 = su.defineHotkey(hotkey_definitions,
                          state_typename, "primitive selector", "o")

    template.bindHotkeyDefinitions(hotkey_definitions)
    template.bindHandle( "xform", "Transform" )

    m = hou.ViewerStateMenu("menu","Polypen")

    m.addSeparator()
    m.addRadioStrip("radio_strip","radio","radio_item1")
    m.addRadioStripItem("radio_strip","radio_item1","Radio1",hk2)
    m.addRadioStripItem("radio_strip","radio_item2","Radio2", hk1)

    template.bindMenu(m)

    template.bindGeometrySelector("geo selector",
        quick_select=True, 
        name="primitive_selector",
        allow_drag=True, 
        auto_start=True, 
        use_existing_selection=True, 
        consume_selection=False, 
        secure_selection=hou.secureSelectionOption.Ignore, 
        initial_selection="", 
        ordered=False, 
        geometry_types=[hou.geometryType.Primitives, hou.geometryType.Points, hou.geometryType.Edges], 
        primitive_types=[], 
        allow_other_sops=False, 
        hotkey=hk2)


    





    return template
