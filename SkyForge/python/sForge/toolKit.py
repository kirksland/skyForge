"""
Description:    Various utilities used modeling tool .
Author:         kirksland
Date Created:   Feb 21, 2024
"""

from sys import displayhook
import hou 
class toolKit:
    def __init__(self):
        """
        Initialisation du tool kit.
        
        :param package_name: Nom du package tel qu'il apparaît dans Houdini (ex: "MonPackage")
        :param package_root: Chemin racine du package (ex: "$HOUDINI_USER_PREF_DIR/packages/MonPackage")
        """
        pass

    def addNode(self, nodeType='null', nodeLabel='my_new_nodeTest'):
            # Récupérer les nœuds sélectionnés
        selected_nodes = hou.selectedNodes()

        if selected_nodes:
            # Prendre le premier nœud sélectionné
            selected_node = selected_nodes[0]
            
            # Récupérer son parent (le network où il est situé)
            parent = selected_node.parent()
            
            # Créer un nouveau nœud (exemple : un nœud 'null')
            new_node = parent.createNode(nodeType, nodeLabel)
            
            # Positionner le nouveau nœud en dessous du nœud sélectionné
            new_node.setPosition(selected_node.position() + hou.Vector2(0, -1))
            
            # Connecter le nouveau nœud à la sortie du nœud sélectionné
            new_node.setInput(0, selected_node)
            
            # Sélectionner le nouveau nœud
            new_node.setSelected(True)
            
            print(f"Création du nœud '{new_node.name()}' après '{selected_node.name()}'")
        else:
            print("Aucun nœud sélectionné.")

    def getOppositeEdge(self, geo, sel_str):
        sel_edges = geo.globEdges(sel_str)
        if not sel_edges:
            raise RuntimeError("Aucun edge trouvé pour le pattern '%s'" % sel_str)

        # Edge de départ
        initial_edge = sel_edges[0]
        init_point = initial_edge.points()

        initial_tuple = (init_point[1].number(), init_point[0].number())

        # Structures de stockage
        visited_edges = set()
        visited_prims = set()
        opposite_edges = []

        # File d'attente pour explorer les deux directions
        queue = [initial_tuple]

        while queue:
            current_edge_tuple = queue.pop(0)  # On prend le premier élément de la liste (BFS)
            if current_edge_tuple in visited_edges:
                continue  # Déjà traité

            # Trouver l'edge courant dans Houdini
            current_edge = geo.findEdge(geo.point(current_edge_tuple[1]), geo.point(current_edge_tuple[0]))
            if not current_edge:
                continue

            visited_edges.add(current_edge_tuple)

            # Récupérer les primitives connectées
            connected_prims = current_edge.prims()
            if not connected_prims:
                continue  # Aucun quad trouvé

            for prim in connected_prims:
                prim_num = prim.number()

                # Vérifier si la primitive a déjà été visitée
                if prim_num in visited_prims:
                    continue

                vertices = prim.vertices()
                if len(vertices) != 4:
                    continue  # Ne traiter que les quadrilatères

                # Construire les edges de la primitive
                prim_edges = []
                for i in range(len(vertices)):
                    v0 = vertices[i].point().number()
                    v1 = vertices[(i + 1) % len(vertices)].point().number()
                    edge_tuple = (v0, v1)
                    prim_edges.append(edge_tuple)

                # Trouver l'edge opposé : celui qui ne partage aucun point avec l'edge courant
                for edge in prim_edges:
                    if set(edge).isdisjoint(set(current_edge_tuple)) and edge not in visited_edges:
                        opposite_edges.append((current_edge_tuple, edge, prim_num))
                        queue.append(edge)  # Ajouter pour continuer l'exploration

                visited_prims.add(prim_num)

        return opposite_edges
    def toggleFlag(self, newNode, previousNode, isSelected=True):
        """
        toggle node flag and selecte 
        :param newNode: node flag to activate
        :param previousNode: node flag to deactivate

        """


        if isSelected == True:
            newNode.setRenderFlag(True)
            newNode.setDisplayFlag(True)
            newNode.setSelected(True)

            previousNode.setRenderFlag(False)
            previousNode.setDisplayFlag(False)
            previousNode.setSelected(False)

        else:

            newNode.setRenderFlag(True)
            newNode.setDisplayFlag(True)
            newNode.setSelected(False)

            previousNode.setRenderFlag(False)
            previousNode.setDisplayFlag(False)
            previousNode.setSelected(True)


    def spawnNode(self, nodeName, Isparent=True):

        viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if viewer:
            current_node = viewer.currentNode()
            node_type = current_node.type()
            definition = node_type.definition()
            if definition is not None :
                name = definition.nodeType()
                tools = definition.tools()
                tool_list = [v for k, v in tools.items()]
                tool = tool_list[0]
                sub = tool.toolMenuLocations()
                print(node_type)
                print(definition)

                print(name)
                print(tools)
                print(sub)

            if current_node.type().category().name() == "Sop":
                if Isparent == True:
                    parent = current_node.parent()
                    if current_node.input(0) is not None:
                        previous_node = current_node.input(0) 
                        
                        previous_node.setTemplateFlag(False)
                    input_number = len(current_node.inputConnectors())

                    if input_number >= 2 and current_node.input(1) is None:
                        new_node = parent.createNode(nodeName)
                        pos = current_node.position()

                        new_node.setPosition([pos[0] + 3, pos[1] + 1])
                       
                        current_node.setInput(1,new_node)
                        self.toggleFlag(current_node, new_node, False)

                        current_node.setTemplateFlag(True)

                        return new_node

                    else:
                        new_node = parent.createNode(nodeName)
                        pos = current_node.position()
                        new_node.setPosition([pos[0], pos[1] - 1])
                        self.toggleFlag(new_node, current_node)
                        current_node.setTemplateFlag(True)
                        new_node.setInput(0,current_node)

                        return new_node
                else:
                    parent = current_node.parent()
                    new_node = parent.createNode(nodeName)
                    new_node.setSelected(True) 
                    pos = current_node.position()
                    new_node.setPosition([pos[0] + 2,pos[1]])
                    current_node.setSelected(False)

            else: 
                parent = current_node
                new_node = parent.createNode(nodeName)
                new_node.setSelected(True)

                return new_node


