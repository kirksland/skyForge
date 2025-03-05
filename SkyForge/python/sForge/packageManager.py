"""
Description:    Various utilities used to manage package .
Author:         kirksland
Date Created:   Feb 21, 2024
"""

import os
import sys
import importlib
import hou
class packageManager:
    def __init__(self,package_name='SkyForgePackage', package_root='$HPD'):
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
        self.hda_dir = os.path.join(self.package_root, "hda")

    def scanFolder(self, folderPath='$HPD/hda', extension='hdanc'):
        """
        Scanne le dossier 'python' du package et retourne la liste des fichiers sans leur extension.
        :param folderPath: chemin d'acces du dossier à scanner
        :param extension: l'extension des fichier recherché 
        """
        
        folder_path = os.path.expandvars(folderPath)
        modules = []
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith('.' + extension):
                    # Enlève l'extension du fichier
                    name_without_extension = os.path.splitext(filename)[0]
                    modules.append(name_without_extension)
            
            # Vérification après la boucle, mais toujours dans le bloc if
            if len(modules) == 0:
                print(f"Aucun fichier avec l'extension {extension} trouvé")
        else:
            print(f"Le dossier {folder_path} n'existe pas.")
        
        return modules

    def reloadPython(self):
        """
            reload all module of sForge
        """
        # Vérifiez les noms complets dans sys.modules
        modules_to_reload = [
            'sForge.packageManager',
            'sForge.toolKit',
            'sForge.customUI',
            'sForge'  # Parent module last
        ]
    
        for module_name in modules_to_reload:
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
                print(f"Module '{module_name}' rechargé!")
            else:
                print(f"Le module '{module_name}' n'est pas dans sys.modules")

    def scanShelfTool(self, toolbar_path, shelf_filename):
        """
        scan the shelfTool at giver location
        """
        import xml.etree.ElementTree as ET

        # Chemin complet vers le fichier shelf
        shelf_path = os.path.join(toolbar_path, shelf_filename)
        # Vérifier si le fichier existe
        if not os.path.exists(shelf_path):
            print(f"Le fichier {shelf_path} n'existe pas")
            return None
        try:
            # Parser le fichier XML
            tree = ET.parse(shelf_path)
            root = tree.getroot()
            
            # Obtenir les informations de base du shelf
            shelf_info = {
                'name': root.get('name', 'Unknown'),
                'label': root.get('label', 'Unknown'),
                'tools': []
            }
            
            # Extraire les informations sur chaque outil
            for tool in root.findall('.//tool'):
                tool_info = {
                    'name': tool.get('name', 'Unknown'),
                    'label': tool.get('label', 'Unknown'),
                    'icon': tool.get('icon', 'None')
                }
                
                # Récupérer le script si disponible
                script_tag = tool.find('./script')
                if script_tag is not None:
                    tool_info['script'] = script_tag.text
                
                shelf_info['tools'].append(tool_info)
            
            print(f"Shelf '{shelf_info['name']}' trouvé avec {len(shelf_info['tools'])} outils")
            for tool in shelf_info['tools']:
                print(f"- {tool['name']}: {tool['label']}")
            
            return shelf_info
        
        except Exception as e:
            print(f"Erreur lors de l'analyse du fichier shelf: {e}")
            return None

            
