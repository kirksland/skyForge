"""
Description:    Various utilities used modeling tool .
Author:         kirksland
Date Created:   Feb 21, 2024
"""

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
        
        # On prend un edge initial pour commencer l'itération
        current_edge = sel_edges[0]
        
        # Set pour éviter les répétitions d'edges et de primitives
        visited_edges = set()
        visited_prims = set()
        
        while current_edge:
            current_edge_pts = {pt.number() for pt in current_edge.points()}
            print("Current edge:", current_edge_pts)
        
            # Récupération des primitives connectées à cet edge
            connected_prims = current_edge.prims()
            if not connected_prims:
                print("Aucune primitive connectée à l'edge courant.")
                break  # Arrêter si aucune primitive n'est trouvée
        
            # Parcourir les primitives pour trouver un edge opposé
            opposite_edge = None
            for prim in connected_prims:
                prim_num = prim.number()  # Numéro de la primitive
        
                # Vérifier si cette primitive a déjà été visitée
                if prim_num in visited_prims:
                    continue  # Si oui, on passe à l'autre primitive
        
                vertices = prim.vertices()
                prim.setAttribValue("Cd", (1.0, 0.0, 0.1))
                
                # Ne traiter que les quadrilatères
                if len(vertices) != 4:
                    continue
        
                # Récupérer tous les edges de la primitive
                prim_edges = []
                for i in range(len(vertices)):
                    v0 = vertices[i].point().number()
                    v1 = vertices[(i + 1) % len(vertices)].point().number()
                    edge_tuple = (v0, v1)
                    prim_edges.append(edge_tuple)
        
                print(f"Edges de la primitive {prim_num}: {prim_edges}")
        
                # Vérifier si la primitive contient l'edge courant
                if not any(set(edge) == current_edge_pts for edge in prim_edges):
                    continue
        
                # Trouver l'edge opposé
                for edge in prim_edges:
                    if set(edge).isdisjoint(current_edge_pts) and edge not in visited_edges:
                        opposite_edge = edge
                        break
        
                if opposite_edge:
                    print(f"Edge opposé trouvé: {opposite_edge}")
                    visited_prims.add(prim_num)  # Ajouter la primitive à l'ensemble des primitives visitées
                    break  # On a trouvé un edge opposé, on sort de la boucle
        
            # Si aucun nouvel edge opposé n'est trouvé, arrêter la boucle
            if not opposite_edge:
                print("Aucun nouvel edge opposé trouvé, fin de l'itération.")
                break
        
            # Affichage du résultat
            print("Nouvel edge sélectionné :", opposite_edge)
        
            visited_edges.add(opposite_edge)
        
            # Mettre à jour `current_edge` pour la prochaine itération
            current_edge = geo.findEdge(geo.point(opposite_edge[0]), geo.point(opposite_edge[1]))
            print(f"Nouvel edge courant: {current_edge}")