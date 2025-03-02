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


    
    def initTransform(self, node):
        for parm_name in self.parm_names:
            node.parm(parm_name).set(0)
       
        node.parm("sx").set(1)
        node.parm("sy").set(1)
        node.parm("sz").set(1)

    def getSelectionIds(self, geo, sel_type, sel_str, handle):
        """ Retourne les identifiants des éléments sélectionnés """
        if sel_type == hou.geometryType.Edges:
            return {
                p.number(): (tuple(p.position()), ((0.0, 0.0, 0.0),(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)), handle)
                for e in geo.globEdges(sel_str)
                for p in e.points()
            }
        elif sel_type == hou.geometryType.Points:
            return {
            p.number(): (tuple(p.position()), ((0.0, 0.0, 0.0),(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)), handle)
            for p in geo.globPoints(sel_str, ordered=False)
        }

        elif sel_type == hou.geometryType.Primitives:
            return {
                p.number(): (tuple(p.position()), ((0.0, 0.0, 0.0),(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)), handle)
                for f in geo.globPrims(sel_str)
                for p in f.points()
            }

    def getBoundingBox(self, geo, sel_type, sel_str):
        """ Retourne la bounding box en fonction du type de sélection """
        if sel_type == hou.geometryType.Primitives:
            return geo.orientedPrimBoundingBox(sel_str)
        elif sel_type == hou.geometryType.Edges:
            edge_points = [p for e in geo.globEdges(sel_str) for p in e.points()]
            return geo.orientedPointBoundingBox(" ".join(str(p.number()) for p in edge_points))
        elif sel_type == hou.geometryType.Points:
            return geo.orientedPointBoundingBox(sel_str)
        return hou.BoundingBox()

    def build_transformation_matrix(self, parms):
        """Construit la matrice de transformation complète."""
        t = (parms["tx"], parms["ty"], parms["tz"])  # Translation
        r = (parms["rx"], parms["ry"], parms["rz"])  # Rotation
        s = (parms["sx"], parms["sy"], parms["sz"])  # Scale

        matrix_list = (t, r, s)

        return matrix_list


        #---------------------------------------------------------------------------
        #---------------------------------------------------------------------------


    def onEnter(self,kwargs):
        """ Called on node bound states when it starts
        """
        node = kwargs["node"]
        state_parms = kwargs["state_parms"]
        self.geometry = node.geometry()
        self.xform_handle.show(False)


    def onExit(self,kwargs):
        """ Called when the state terminates
        """
        state_parms = kwargs["state_parms"]

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

        # Récupérer les données précédentes stockées dans le parm "transform_data"
        old_data_str = node.parm("transform_data").eval()
        old_data = json.loads(old_data_str or "{}")

        # Vérifier s'il y a des sélections
        if "selections" in old_data:
            # Récupérer la dernière sélection
            last_selection = old_data["selections"][-1]  # Le dernier élément de la liste "selections"

            # Accéder à "ids" qui est un dictionnaire retourné par getSelectionIds
            selection = last_selection["ids"]
            for last_key, last_value in selection.items():
                # Accéder au premier sous-tuple (position du point)
                position = last_value[0]  # Premier sous-tuple : position du point    

                # Mettre à jour la valeur dans le dictionnaire
                selection[last_key] = (last_value[0], last_value[1], tuple(newp))
                
            # Mettre à jour old_data avec les nouvelles valeurs
            old_data["selections"][-1]["ids"] = selection
            node.parm("transform_data").set(json.dumps(old_data))

        self.scene_viewer.endStateUndo()
        
    def onHandleToState(self, kwargs):
        """ Sets the node parms with the handle parms.
        """
        parms = kwargs["parms"]
        node = kwargs["node"]  

        final_matrix = self.build_transformation_matrix(parms)
        pivot = (parms["px"], parms["py"], parms["pz"])
        

        # Récupérer les données précédentes stockées dans le parm "transform_data"
        old_data_str = node.parm("transform_data").eval()
        old_data = json.loads(old_data_str or "{}")

        # Vérifier s'il y a des sélections
        if "selections" in old_data:
            # Récupérer la dernière sélection
            last_selection = old_data["selections"][-1]  # Le dernier élément de la liste "selections"

            # Accéder à "ids" qui est un dictionnaire retourné par getSelectionIds
            selection = last_selection["ids"]
            for last_key, last_value in selection.items():
                # Accéder au premier sous-tuple (position du point)
                position = last_value[0]  # Premier sous-tuple : position du point    

                # Mettre à jour la valeur dans le dictionnaire
                selection[last_key] = (last_value[0], final_matrix, pivot)  # On met à jour le second sous-tuple
                

            # Mettre à jour old_data avec les nouvelles valeurs
            old_data["selections"][-1]["ids"] = selection

            # Mettre à jour le parm transform_data avec le nouveau JSON
            node.parm("transform_data").set(json.dumps(old_data))
            

        for parm_name in self.parm_names:
            node.parm(parm_name).set(parms[parm_name])

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
        selection, node, state_parms = kwargs["selection"], kwargs["node"], kwargs["state_parms"]
        geo = self.geometry
        self.initTransform(node)
        normal = hou.Vector3()


        if not selection or not selection.selectionStrings():
            self.xform_handle.show(False)
            return False

        if selection is not None:
            geo = node.geometry()

            sel_type = selection.geometryType()
            sel_ids = selection
            sel_str = selection.selectionStrings()[0]
            bbox = self.getBoundingBox(geo, sel_type, sel_str)
            handlePos = (bbox.center()[0], bbox.center()[1], bbox.center()[2])
            old_data_str = node.parm("transform_data").eval()   

            old_data = json.loads(node.parm("transform_data").eval() or "{}")
            old_data.setdefault("selections", [])

            selection = self.getSelectionIds(geo, sel_type, sel_str, handlePos)
            last_key, last_value = list(selection.items())[-1]  # Récupérer le dernier élément du dictionnaire (par exemple)
            position = last_value[0]  # Accéder au premier sous-tuple (position du point)
            
            selection_data = {
            "type": str(sel_type),
            "ids": self.getSelectionIds(geo, sel_type, sel_str, handlePos),
            "state": "selection"
            }
            old_data["selections"].append(selection_data)
            node.parm("transform_data").set(json.dumps(old_data))


            if "selections" in old_data:
                # Récupérer la dernière sélection
                last_selection = old_data["selections"][-1]  # Le dernier élément de la liste "selections"

                # Accéder à "ids" qui est un dictionnaire retourné par getSelectionIds
                selection = last_selection["ids"]
                for last_key, last_value in selection.items():
                    pt = geo.point(int(last_key))
                    normal += hou.Vector3(pt.attribValue("N"))
            viewerAxis = hou.Vector3(0.0, 1.0, 0.0)
            rotation = alignVector(viewerAxis, normal)
            # Mettre à jour les paramètres du nœud
            node.parmTuple("p").set(bbox.center())
            node.parmTuple("pivot_r").set(rotation)
            

            #node.parmTuple("pivot_r").set(rotation)

            self.xform_handle.show(True)
            self.xform_handle.update()
        
        # Must return True to accept the selection
        return False

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
