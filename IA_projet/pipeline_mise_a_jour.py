"""Fonction qui met à jour le csv avec les nouveaux articles
"""
# Obtenir le chemin absolu du fichier en cours d'exécution
import os
import sys
current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(os.path.dirname(current_file_path))
extractor_path = os.path.join(current_directory, 'Extractor')
sys.path.append(extractor_path)
import scrapp_to_csv
import load_data
import load_data_sc