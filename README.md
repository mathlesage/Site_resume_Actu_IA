**README - Projet Django : Scraping et Résumé Automatique d'Articles d'Actualité sur l'IA**

**Description**

Ce projet Django a pour but de scrapper les informations provenant de sites d'actualités sur l'intelligence artificielle (IA), de générer automatiquement un résumé des articles via un modèle de langage large (LLM) et de publier ces résumés sur le site web. Le projet est conçu pour automatiser la collecte, la synthèse et la publication d'articles, afin de maintenir les utilisateurs informés des dernières tendances et actualités dans le domaine de l'IA.

**⚠️ Remarque importante : La partie du code concernant la génération de résumés a été omise et ajoutée au .gitignore car elle contient des éléments propriétaires développés pour une entreprise. Cette section peut donc être implémentée séparément ou remplacée selon les besoins.**


Fonctionnalités :

Scraping d'articles d'actualités sur l'IA : Collecte automatique des articles provenant de plusieurs sites web spécialisés en IA .

Résumé automatique avec LLM : Les articles récupérés sont résumés à l'aide d'un modèle de langage large (llama-3-8b) afin de condenser l'information et fournir des résumés clairs et précis.

Publication sur le site : Les résumés sont ensuite publiés sur un site web accessible via l'interface utilisateur Django.

Système de gestion des articles : Interface d'administration Django pour consulter, modifier, supprimer ou approuver les résumés avant publication.

Prérequis :
Python 3.x
Django 3.x ou supérieur
Un modèle LLM pour la génération automatique de résumés
