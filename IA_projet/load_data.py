
from pathlib import Path
import os
import django
import csv
BASE_DIR = Path(__file__).resolve().parent

CHEMIN_CSV = BASE_DIR / "data_resume.csv"

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IA_projet.settings')
django.setup()

from myapp.models import Article

# Supprimer tous les anciens articles
Article.objects.all().delete()

# Charger de nouveaux articles depuis le fichier CSV
with open(CHEMIN_CSV, newline='',encoding='cp1252') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    for row in reader:
        title = row['titre']
        date = row['date']  # Utiliser row['date'] tel quel
        summary = row['resume']
        resume_tr = row.get('resume_tr', '')
        url = row['url']
        print(summary)
        # Créer un nouvel article
        Article.objects.create(title=title, date=date, summary=summary, resume_tr=resume_tr, url=url)
