"""
State:          PolypenV2
State type:     polypenV2
Description:    PolypenV2
Author:         justi
Date Created:   February 13, 2025 - 01:05:41
"""

import sForge
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
        self.geometry = None
        self.xform_handle = hou.Handle(self.scene_viewer, "Transform")
        self.parm_names = [
        "tx", "ty", "tz", 
        "rx", "ry", "rz", 
        "sx", "sy", "sz", 
        "px", "py", "pz", 
        "pivot_rx", "pivot_ry", "pivot_rz"
        ]

        self.gi = None
    def initTransform(self, node):
        for parm in self.parm_names:
            node.parm(parm).set(1 if parm.startswith("s") else 0)

    def getPointIds(self, geo, sel_type, sel_str):
        """
        retourne les identifiant des points des elements selectionner
        
        :param geo: hou.geometry
        :param sel_type: selection object 
        :param sel_str: the string send by selectionEvent 
        """

        if sel_type == hou.geometryType.Points:
            return {p for p in geo.globPoints(sel_str, ordered=False)}
        elif sel_type == hou.geometryType.Edges:
            return  {p for e in geo.globEdges(sel_str)  for p in e.points()}
        elif sel_type == hou.geometryType.Primitives:
            return  {p for f in geo.globPrims(sel_str)  for p in f.points()}

    def setDataIds(self, ids, handle):
        """ Retourne un dictionnaire de tupple pour configurer la transformation """
        return{
        p.number(): (tuple(p.position()), ((0.0, 0.0, 0.0),(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)), handle)
        for p in ids
        }

    def getBoundingBox(self, geo, sel_type, sel_str):
        """ Retourne la bounding box en fonction du type de sélection """
        if sel_type == hou.geometryType.Primitives:
            return geo.primBoundingBox(sel_str)
        elif sel_type == hou.geometryType.Edges:
            edge_points = [p for e in geo.globEdges(sel_str) for p in e.points()]
            return geo.pointBoundingBox(" ".join(str(p.number()) for p in edge_points))
        elif sel_type == hou.geometryType.Points:
            return geo.pointBoundingBox(sel_str)
        return hou.BoundingBox()

    def build_transformation_matrix(self, parms):
        """Construit la matrice de transformation complète."""
        t = (parms["tx"], parms["ty"], parms["tz"])  # Translation
        r = (parms["rx"], parms["ry"], parms["rz"])  # Rotation
        s = (parms["sx"], parms["sy"], parms["sz"])  # Scale

        matrix_list = (t, r, s)

        return matrix_list


    def normal(self, geo, sel_type, sel_str):
        normal = hou.Vector3()
        if sel_type == hou.geometryType.Primitives:

            prim = geo.globPrims(sel_str)
            for p in prim:
                vertices = geo.globVertices(str(p.number()))
                for v in vertices:
                    n = v.attribValue("N")
                    normal += hou.Vector3(n)
                    
        elif sel_type == hou.geometryType.Points:
            # Récupérer les points via la chaîne (ex: "0 1 2 3")
            
            points = geo.globPoints(sel_str)
            ids = [p.number() for p in points]
            ids_set = set(ids)

            if len(ids_set) < 4 :
                for p in points:
                    v = p.vertices()
                    for ve in v:
                        n = ve.attribValue("N")
                        normal += hou.Vector3(n)
            else:           
                # Récupérer toutes les primitives associées aux points de la sélection
                prims_set = set()
                for pt in points:
                    for prim in pt.prims():
                        prims_set.add(prim)

                # Filtrer pour ne garder que les primitives qui contiennent au moins 4 points de la sélection
                internal_prims = []
                for prim in prims_set:
                    prim_ptID = set()
                    for pt in prim.points():
                        prim_ptID.add(pt.number())
                    # Calculer l'intersection entre les IDs de la sélection et ceux de la primitive
                    common_ids = ids_set.intersection(prim_ptID)
                    if len(common_ids) >= 4:
                        internal_prims.append(prim)

                # Afficher le résultat

                for p in internal_prims:
                    vertices = geo.globVertices(str(p.number()))
                    for v in vertices:
                        n = v.attribValue("N")
                        normal += hou.Vector3(n)
                    
        elif sel_type == hou.geometryType.Edges:
            edges = geo.globEdges(sel_str)
            edge_set = set()
            for edge in edges:
                edge_point = edge.points()
                for p in edge_point:
                    edge_set.add(p.number())

            for p in edge_set:
                point = geo.point(p)
                v = point.vertices()
                for ve in v:
                    n = ve.attribValue("N")
                    normal += hou.Vector3(n) 
        return normal
        #---------------------------------------------------------------------------
        #---------------------------------------------------------------------------

    def onEnter(self,kwargs):
        """ Called on node bound states when it starts
        """
        node, state_parm = kwargs["node"], kwargs["state_parms"]
        self.geometry = node.geometry()
        self.xform_handle.show(False)
        self.gi = su.GeometryIntersector(self.geometry, self.scene_viewer)
        print(dir(self.gi))
        

    def onExit(self,kwargs):
        """ Called when the state terminates
        """
        state_parms = kwargs["state_parms"]

    def onSelection(self, kwargs):
        """ Called when a selector has selected something
        """   
        selection, node = kwargs["selection"], kwargs["node"]
        geo = self.geometry
        self.initTransform(node)


        if not selection or not selection.selectionStrings():
            self.xform_handle.show(False)
            return False

        sel_type = selection.geometryType()
        sel_str = selection.selectionStrings()[0]
        ids = self.getPointIds(geo, sel_type, sel_str)


        normal = self.normal(geo, sel_type, sel_str)

        """
        normal = hou.Vector3()
        for pt in ids:
            n = pt.attribValue("Vn")
            normal += hou.Vector3(n)
        """   
        handlePos = tuple(self.getBoundingBox(geo, sel_type, sel_str).center())
        handleRot = tuple(alignVector(hou.Vector3(0,1,0),normal))

        handle = (handlePos,handleRot)

        old_data = json.loads(node.parm("transform_data").eval() or "{}")
        old_data.setdefault("selections", [])

        selection_data = {
        "type": str(sel_type),
        "ids": self.setDataIds(ids, handle)
        }

        old_data["selections"].append(selection_data)
        node.parm("transform_data").set(json.dumps(old_data))
        
        # Mettre à jour les paramètres du nœud
        node.parmTuple("p").set(handlePos)
        node.parmTuple("pivot_r").set(handleRot)
        self.xform_handle.show(True)
        self.xform_handle.update()

        
        return False 

    def onHandleToState(self, kwargs):
        """ Sets the node parms with the handle parms.
        """
        parms = kwargs["parms"]
        node = kwargs["node"]  

        old_data_str = node.parm("transform_data").eval()                                           # Récupérer les données précédentes stockées dans le parm "transform_data"
        old_data = json.loads(old_data_str or "{}")
        if old_data:
            offset_matrix = self.build_transformation_matrix(parms)                                     # creer un tupple qui represente les parametres de notre matrice
            pivot = ((parms["px"], parms["py"], parms["pz"]),(parms["pivot_rx"], parms["pivot_ry"], parms["pivot_rz"]))

            last_selection = old_data["selections"][-1]                                                 # dernier élément de la liste "selections"
            selection = last_selection["ids"]                       
            for key, value in selection.items():
                selection[key] = (value[0], offset_matrix, pivot)                                        # On met à jour le second sous-tuple
            old_data["selections"][-1]["ids"] = selection

            node.parm("transform_data").set(json.dumps(old_data))                                        # Mettre à jour le parm transform_data avec le nouveau JSON
            for parm_name in self.parm_names:
                node.parm(parm_name).set(parms[parm_name])

    def onBeginHandleToState(self, kwargs):
        """ Open an undo bracket for the handle operations.
        """
        self.scene_viewer.beginStateUndo("Geo Deformer Interaction")        

    def onEndHandleToState(self, kwargs):
        """ Close the handle undo bracket.
        """
        node = kwargs["node"]  
        t = node.parmTuple("t").eval()
        p = node.parmTuple("p").eval()
        newp = hou.Vector3(t) + hou.Vector3(p)


        old_data_str = node.parm("transform_data").eval()   # Récupérer les données précédentes stockées dans le parm "transform_data"
        old_data = json.loads(old_data_str or "{}")

        # Vérifier s'il y a des sélections
        if "selections" in old_data:
            
            last_selection = old_data["selections"][-1]  # dernier élément de la liste "selections"
            selection = last_selection["ids"]            # Accéder à "ids" qui est un dictionnaire retourné par setDataIds

            for last_key, last_value in selection.items():
                selection[last_key] = (last_value[0], last_value[1], tuple(newp))   # Mettre à jour la valeur dans le dictionnaire
            old_data["selections"][-1]["ids"] = selection
        self.scene_viewer.endStateUndo()
        
    def onStateToHandle(self, kwargs):
        """ Sets the handle parms with the node parms.
        """                       
        node = kwargs["node"]
        parms = kwargs["parms"]        
        for parm_name in self.parm_names:
            parms[parm_name] = node.parm(parm_name).eval()        
        self.xform_handle.show(True)

    def onMouseEvent(self, kwargs):
        """ Process mouse and tablet events
        """
        ui_event = kwargs["ui_event"]
        dev = ui_event.device()
        #print("________________________",dev)
        rorigin, rdir = ui_event.ray()

        intersect = self.gi.intersect(rorigin, rdir)
        if intersect != 0 and dev.isShiftKey():
            closest_edge = self.gi._closest_edge()
            if closest_edge is not None:
                if self.gi._distance_to_edge(self.gi.position, closest_edge) < 0.01 :
                    closest_edge_id = closest_edge.edgeId()
                    forge = sForge.toolKit()
                    opposite_edge = forge.getOppositeEdge(self.geometry, closest_edge.edgeId())
                    print(opposite_edge)



    def onMenuAction(self, kwargs):
        menuItems = kwargs["menu_item"]
        if menuItems == "clean":
            kwargs["node"].hdaModule().reset(kwargs["node"])
    
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


def createViewerStateTemplate():
    """ Mandatory entry point to create and return the viewer state 
        template to register. """

    state_typename = "polypenV2"
    state_label = "PolypenV2"
    state_cat = hou.sopNodeTypeCategory()

    template = hou.ViewerStateTemplate(state_typename, state_label, state_cat)
    template.bindFactory(State)
    template.bindIcon("$SK_ICONS/polyPen4.png")

    hotkey_definitions = hou.PluginHotkeyDefinitions()
    hk1 = su.defineHotkey(hotkey_definitions,
                          state_typename, "drawable selector", "k")
    hk2 = su.defineHotkey(hotkey_definitions,
                          state_typename, "primitive selector", "o")

    template.bindHotkeyDefinitions(hotkey_definitions)
    template.bindHandle( "xform", "Transform" )

    m = hou.ViewerStateMenu("menu","Polypen")
    m.addActionItem("clean","Clean transform")

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
