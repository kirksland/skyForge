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
