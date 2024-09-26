import os
import subprocess
from django.shortcuts import render
from django.http import JsonResponse
from .models import Article, Article_scientifique


current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(os.path.dirname(current_file_path))
FILE_DIRECTOR=current_directory + "\\pipeline_mise_a_jour.py"


def run_python_function(request):
    # Lancer la fonction Python (par exemple, un script)
    try:
        # Supposons que la fonction est un script que nous devons exécuter
        subprocess.run(["python3", FILE_DIRECTOR], check=True)
        return JsonResponse({'status': 'success', 'message': 'Fonction compilée avec succès!'})
    except subprocess.CalledProcessError as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
    
def home_view(request):
    # Récupérer tous les articles depuis la base de données
    articles = Article.objects.all()
    # Passer les articles au template 'articles.html'
    return render(request, 'articles.html', {'articles': articles})

def data_view(request):
    # Convertir les articles en liste de dictionnaires pour JSON
    data = list(Article.objects.values())
    # Retourner les données au format JSON
    return JsonResponse(data, safe=False)

def articles_view(request):
    # Récupérer tous les articles depuis la base de données
    articles = Article.objects.all()
    # Passer les articles au template 'articles.html'
    return render(request, 'articles.html', {'articles': articles})

def translate_summary(request, article_id):
    try:
        # Essayer de récupérer l'article par son ID
        article = Article.objects.get(id=article_id)
        # Retourner la traduction du résumé ou un message par défaut si la traduction est absente
        response_data = {
            'resume_tr': article.resume_tr if article.resume_tr else 'Traduction non disponible'
        }
    except Article.DoesNotExist:
        # Si l'article n'existe pas, retourner une erreur
        response_data = {
            'error': 'Article not found'
        }
    # Retourner les données au format JSON
    return JsonResponse(response_data)


def index_view(request):
        # Récupérer tous les articles depuis la base de données
    articles = Article_scientifique.objects.all()
        # Passer les articles au template 'articles.html'
    return render(request, 'index.html', {'articles': articles})




