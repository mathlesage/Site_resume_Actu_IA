from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    date = models.CharField(max_length=100)  # Utilisation d'un CharField pour la date
    summary = models.TextField()
    resume_tr = models.TextField(blank=True, null=True)  # Champ pour le résumé traduit
    url = models.URLField()

    def __str__(self):
        return self.title

class Article_scientifique(models.Model):
    title = models.CharField(max_length=200)
    date = models.CharField(max_length=100)  # Utilisation d'un CharField pour la date
    summary = models.TextField()
    resume_tr = models.TextField(blank=True, null=True)  # Champ pour le résumé traduit
    url = models.URLField()

    def __str__(self):
        return self.title