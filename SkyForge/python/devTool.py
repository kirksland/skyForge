import os
import sys
import importlib
import hou

class PackageManager:
    def __init__(self,package_name, package_root):
        """
        Initialisation du gestionnaire de package.
        
        :param package_name: Nom du package tel qu'il apparaît dans Houdini (ex: "MonPackage")
        :param package_root: Chemin racine du package (ex: "$HOUDINI_USER_PREF_DIR/packages/MonPackage")
        """

        self.package_name = package_name
        # Résolution des variables d'environnement Houdini dans le chemin
        self.package_root = hou.expandString(package_root)
        # Dossier contenant les scripts Python
        self.python_dir = os.path.join(self.package_root, "python")

    def scanPythonFolder(self):
        """
        Scanne le dossier 'python' du package et retourne la liste des fichiers .py.
        """
        modules = []
        if os.path.isdir(self.python_dir):
            for filename in os.listdir(self.python_dir):
                if filename.endswith(".py"):
                    modules.append(filename)
        else:
            print(f"Le dossier {self.python_dir} n'existe pas.")
        return modules

    def reloadPython(self):

        module_name = "sForge"
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
            print(f"Python module'{module_name}' rechargé!")


    def reload_package(self):
        """Recharge le package Houdini."""
        try:
            hou.ui.reloadPackage(self.package_name)
            print(f"Package {self.package_name} rechargé avec succès.")
        except Exception as e:
            print(f"Erreur lors du rechargement du package {self.package_name} : {e}")


    def addNode(self, nodeType,nodeLabel):
            # Récupérer les nœuds sélectionnés
        selected_nodes = hou.selectedNodes()

        if selected_nodes:
            # Prendre le premier nœud sélectionné
            selected_node = selected_nodes[0]
            
            # Récupérer son parent (le network où il est situé)
            parent = selected_node.parent()
            
            # Créer un nouveau nœud (exemple : un nœud 'null')
            new_node = parent.createNode('null', 'my_new_nodeTest')
            
            # Positionner le nouveau nœud en dessous du nœud sélectionné
            new_node.setPosition(selected_node.position() + hou.Vector2(0, -1))
            
            # Connecter le nouveau nœud à la sortie du nœud sélectionné
            new_node.setInput(0, selected_node)
            
            # Sélectionner le nouveau nœud
            new_node.setSelected(True)
            
            print(f"Création du nœud '{new_node.name()}' après '{selected_node.name()}'")
        else:
            print("Aucun nœud sélectionné.")