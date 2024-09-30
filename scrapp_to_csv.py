from io import BytesIO
from pathlib import Path
import sys
import time
import PyPDF2
from openai import OpenAI
import pandas as pd
import requests
from bs4 import BeautifulSoup
from Extractor import *
from asyncio import *
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
DetectorFactory.seed = 0
import config
_api_config = config.get_api_config()
_api_key = _api_config['api_key']
_api_endpoint = _api_config['api_endpoint']


CHEMIN_COURANT = Path(sys.argv[0]).resolve().parent.parent /"Extractor"
CHEMIN_VERS_CSV = CHEMIN_COURANT.parent /"IA_projet" /"data_resume.csv"
CHEMIN_VERS_CSV_SCIENTIFIQUE = CHEMIN_COURANT.parent /"IA_projet" /"data_resume_scientifique.csv"

def detect_language(text: str) -> str:
    """Détecte la langue du texte

    Args:
        text (str): texte

    Returns:
        str: si c'est du francais ou de l'anglais ou autre
    """
    try:
        lang = detect(text)
        if lang == 'en':
            return 'anglais'
        elif lang == 'fr':
            return 'francais'
        else:
            return 'autre'
    except LangDetectException:
        return 'Langue indétectable'


def recuperer_url_sans_classe(page: str, balise: str, url: str) -> list[list[str]]:

    soup = BeautifulSoup(page, 'html.parser')
    arxiv_results = soup.find_all('li', class_='arxiv-result')
    tout=[]
    for i in arxiv_results:
        titre=i.find(class_="title is-5 mathjax").text.strip()
        date=i.find("p",class_="is-size-7").text.strip().replace("Submitted","").split(";")[0]
        title_element = i.find(class_=balise)
        
        balise_span=title_element.find("span")
        balise_a=balise_span.find("a")
        if balise_a["href"][0:3] == "htt":
                href=balise_a["href"]
        else:
                href=f'{url}{balise_a["href"]}'
        tout.append([href,titre,date])
    return tout


def read_text_from_file(file_path: str) -> str:
    """ouvre un fichier texte et le renvoie sous forme str

    Args:
        file_path (str): chemin vers le fichier texte

    Returns:
        str: le texte en str du fichier
    """    
    with open(file_path, "r", encoding='utf-8') as file:
        content = file.read()
    return content


def date_t(texte: str) -> str:
    #print(f"{NOMBRE_GENERATION} génération")
    """Fonction qui extrait la date du text avec ligthon

    Args:
        texte ou il y a une date

    Returns:
        Retourn la date sous le format YYYY-MM-DD
    """
    prompt = f"Retourne uniquement la date avec le format YYYY-MM-DD: \n{texte}"

 
    client = OpenAI(api_key=_api_key, base_url=_api_endpoint)
       
    
    appel_model = client.chat.completions.create(
    
    model="alfred-40b-1123",

    messages=[

        {"role": "system", "content" : f"Tu extraits la date et tu la renvoie dans le format YYYY-MM-DD"},

        {"role":"user", "name":"fiche_de_poste",
        "content":prompt}],

    temperature = 0.0)

    generation = appel_model.choices[0].message.content

    return generation


def traduction(texte: str) -> str:
    """Fonction qui traduit le texte

    Args:
        texte à traduire

    Returns:
        Retourn le texte traduit par llama
    """
    prompt=f"Retourne la traduction de ce texte en francais en gardant les termes techenique en anglais: \n{texte}"

 
    client = OpenAI(api_key=_api_key, base_url=_api_endpoint)
       
    
    appel_model = client.chat.completions.create(
    
    model="alfred-40b-1123", #alfred-vllm

    messages=[

        {"role": "system", "content" : f"Tu traduis les textes en francais"},

        {"role":"user", "name":"fiche_de_poste",
        "content":prompt}],

    temperature = 0.0)

    generation = appel_model.choices[0].message.content

    return generation


def resumer_francais(chemin_fichier: str) -> str:
    """Fait un résumé des textes avec llama et un chainage de prompt

    Args:
        chemin_fichier (str): chemin du fichier text à rendre petit

    Returns:
        str: le résumé
    """    
    text = read_text_from_file(chemin_fichier)

    Intermediate_prompt = """

    Votre tâche consiste à fournir un résumé en francais concis et précis d'un document spécifique en se basant sur les informations clés et générales qui s'y trouvent. Le résumé doit être exempt de toute information non pertinente ou erronée et doit offrir des éléments significatifs pour comprendre le thème principal du document. Il doit encapsuler les idées principales et les détails les plus substantiels de manière compacte, permettant au lecteur de comprendre l'objectif et le contenu du document efficacement. Voici comment structurer votre tâche sous forme de liste numérotée :

    1. Idées clés : Extraire et lister les points les plus critiques du document. Cela peut inclure des arguments, théories, observations ou découvertes.

    2. Détails de soutien : Mettre en évidence les détails cruciaux qui soutiennent les idées clés mentionnées précédemment. Ces détails doivent ajouter de la substance au résumé tout en évitant les informations superflues.

    3. Perspectives ou conclusions : Écrire les perspectives importantes, conclusions ou implications tirées du document. Si des recommandations sont faites dans le document, les inclure ici.

    4. Objectif du document : Expliquer brièvement l'objectif ou le but global du document en se basant sur les informations recueillies.

    Assurez-vous que votre résumé soit bref mais exhaustif, présentant le thème principal et les points saillants du document de manière cohérente. Vérifiez également que les informations fournies dans le résumé reflètent correctement le contenu du document et ne contiennent aucune erreur ou détail non pertinent. Votre résumé doit permettre à quelqu'un qui n'a pas lu le document de comprendre son essence et ses points principaux.
    Texte à analyser : 

    ```
    {COMPETITOR_TEXT}
    ```

    Resultat:"""

    Final_prompt="""


    Votre tâche consiste à fournir un résumé concis et précis d'un document spécifique en se basant sur les informations clés et générales qui s'y trouvent. Le résumé doit être exempt de toute information non pertinente ou erronée et doit offrir des éléments significatifs pour comprendre le thème principal du document. Il doit encapsuler les idées principales et les détails les plus substantiels de manière compacte, permettant au lecteur de comprendre l'objectif et le contenu du document efficacement. Le résultat doit être un texte simple couvrant ces éléments :

    Assurez-vous que votre résumé soit bref mais exhaustif, présentant le thème principal et les points saillants du document de manière cohérente. Vérifiez également que les informations fournies dans le résumé reflètent correctement le contenu du document et ne contiennent aucune erreur ou détail non pertinent. Votre résumé doit permettre à quelqu'un qui n'a pas lu le document de comprendre son essence et ses points principaux. Voici le texte à analyser :


    ```
    {COMPETITOR_TEXT}
    ```
    Assurez-vous que le résultat final soit un paragraphe cohérent qui incorpore tous les éléments nécessaires. Commencez par introduire le contenu du document, suivi d'une intégration fluide de ses idées clés, détails de soutien, perspectives ou conclusions, et l'objectif du document. Souvenez-vous de maintenir un flux naturel dans le texte, en évitant les transitions abruptes entre les sujets. Si certaines informations ne sont pas disponibles, continuez simplement sans les intégrer ou tenter de combler les lacunes avec des détails inventés. L'objectif est de créer un résumé à la fois informatif et reflétant le contenu du document, permettant à une personne non familière avec le document de saisir son essence et ses points principaux sans effort.

    Maintenant, donnez-moi un résumé détaillé du contenu global du livre. Chaque élément mentionné ci-dessus doit se retrouver ou être résumé dans le résumé final. Tous les éléments du texte ci-dessous proviennent du même document ; vous devez uniquement en donner un résumé détaillé, même s'il y a des points numérotés, ils proviennent du même livre et ne doivent pas être dans une liste par la suite. Vous devez simplement générer le résumé global basé sur le texte fourni. Structurez le résumé de manière pratique et facile à lire.

    Résumé très détaillé et concis du contenu :"""

    extractor = TextExtractor(model="llama-3-8b",prompt_intermediate=Intermediate_prompt, prompt_final=Final_prompt,text=text,full_compute=True,save_logs=True)
    final_summary,logs = asyncio.run(extractor.run_with_status_updates())

    return final_summary
    
def resumer_anglais(chemin_fichier: str) -> str:
    """Fait un résumé des textes en anglais avec llama et un chainage de prompt

    Args:
        chemin_fichier (str): chemin du fichier text à rendre petit

    Returns:
        str: le résumé
    """ 
    text = read_text_from_file(chemin_fichier)

    Intermediate_prompt = """

    Your task is to provide a concise and accurate summary of a specific document based on its key and general information. The summary should be free of any irrelevant or incorrect information and should offer significant elements to understand the main theme of the document. It should encapsulate the main ideas and the most substantial details compactly, allowing the reader to understand the document's purpose and content effectively. Here is how to structure your task in a numbered list:

    1. Key Ideas: Extract and list the most critical points from the document. This can include arguments, theories, observations, or findings.

    2. Supporting Details: Highlight crucial details that support the key ideas mentioned above. These details should add substance to the summary while avoiding superfluous information.

    3. Perspectives or Conclusions: Write down the important perspectives, conclusions, or implications drawn from the document. If recommendations are made in the document, include them here.

    4. Purpose of the Document: Briefly explain the overall objective or goal of the document based on the gathered information.

    Ensure that your summary is brief yet comprehensive, presenting the main theme and highlights of the document coherently. Also, verify that the information provided in the summary accurately reflects the document's content and does not contain any errors or irrelevant details. Your summary should enable someone who has not read the document to understand its essence and main points.
    Text to analyze: 

    ```
    {COMPETITOR_TEXT}
    ```

    Result: """

    Final_prompt = """

    Your task is to provide a concise and accurate summary of a specific document based on its key and general information. The summary should be free of any irrelevant or incorrect information and should offer significant elements to understand the main theme of the document. It should encapsulate the main ideas and the most substantial details compactly, allowing the reader to understand the document's purpose and content effectively. The result should be a simple text covering these elements:

    Ensure that your summary is brief yet comprehensive, presenting the main theme and highlights of the document coherently. Also, verify that the information provided in the summary accurately reflects the document's content and does not contain any errors or irrelevant details. Your summary should enable someone who has not read the document to understand its essence and main points. Here is the text to analyze:

    ```
    {COMPETITOR_TEXT}
    ```
    Ensure that the final result is a coherent paragraph that incorporates all necessary elements. Start by introducing the content of the document, followed by a smooth integration of its key ideas, supporting details, perspectives or conclusions, and the document's purpose. Remember to maintain a natural flow in the text, avoiding abrupt transitions between subjects. If certain information is unavailable, simply continue without incorporating it or attempting to fill gaps with invented details. The goal is to create a summary that is both informative and reflective of the document's content, enabling someone unfamiliar with the document to grasp its essence and main points effortlessly.

    Now, provide a detailed summary of the overall content of the book. Each element mentioned above should be included or summarized in the final summary. All elements of the text below come from the same document; you only need to provide a detailed summary, even if there are numbered points, they come from the same book and should not be in a list afterward. You should simply generate the overall summary based on the provided text. Structure the summary in a practical and easy-to-read manner.

    Very detailed and concise summary of the content:"""

    # Usage example
    extractor = TextExtractor(model="llama-3-8b",prompt_intermediate=Intermediate_prompt, prompt_final=Final_prompt,text=text,full_compute=True,save_logs=True)
    final_summary, logs = asyncio.run(extractor.run_with_status_updates())

    return final_summary

def recuperer_pdf(url: str) -> str:
        # Télécharger le fichier PDF
    response = requests.get(url)
    pdf_file = BytesIO(response.content)

    # Ouvrir et lire le fichier PDF
    reader = PyPDF2.PdfReader(pdf_file)
    num_pages = len(reader.pages)
    text_pdf=""
    # Extraire le texte de chaque page
    for page_num in range(num_pages):
        page = reader.pages[page_num]
        text_pdf  += page.extract_text() + "\n"
    return text_pdf


def recuperer_page(url: str) -> str:
    """récupère une page et son contenue en format texte

    Args:
        url (str): url de la page

    Returns:
        str: le contenue de la page
    """    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Vérifier que la requête a réussi

    return response.text


def recuperer_url(page: str, balise: str, url: str) -> list[str]:
    """fonction qui récupère les url de la balise et qui renvoie le bon url

    Args:
        page (str): page web
        balise (str): balise de type a qui contient l'url voulu
        url (str): url de la page, sert quand l'url récuperer ne possède pas le nom de domaine

    Returns:
        list[str]: listes des urls
    """
    soup = BeautifulSoup(page, 'html.parser')
    title_element = soup.findAll('a', class_=balise)
    hrefs = []
    for i in title_element:
        if i["href"][0:3] == "htt":
             hrefs.append(i["href"])
        else:
            hrefs.append(f'{url}{i["href"]}')

    return hrefs


def recuperer_text(page: str, balise: str) -> str:
    """Récupère le texte qui est contenue dans la balise de la page

    Args:
        page (str): page web
        balise (str): balise contenue dans la page

    Returns:
        str: le texte de la balise
    """    
    soup = BeautifulSoup(page, 'html.parser')
    title_element = soup.find(class_=balise)
    if title_element:
        return title_element.text.strip()  # Strip to remove any leading/trailing whitespace
    else:
        return ""
    

def recuperer_text_plusieur(page: str, balise: str) -> str:
    """Récupère le texte qui est contenue dans toutes les balise de la page

    Args:
        page (str): page web
        balise (str): balise contenue dans la page

    Returns:
        str: le texte de la balise
    """    
    soup = BeautifulSoup(page, 'html.parser')
    title_element = soup.findAll(class_=balise)
    a = ""

    for i in title_element:
        a += i.text.strip() + "\n"
    
    if a:
        return a 
    else:
        return ""


def mettre_csv(titre: str, date: str, text: str, url: str, CHEMIN_VERS_CSV: str = CHEMIN_VERS_CSV) -> str:
    """Une fonction qui fait le café, 
    elle vérifie si le résumé n'y est pas déjà s'il n'y est pas 
    elle fait un résumé et le traduit puis mets toutes les infos dans un csv

    Args:
        titre (str): titre de la page
        date (str): date de la page
        text (str): texte de la page
        url (str): url de la page

    Returns:
        str: gestion d'erreur
    """    
    df = pd.read_csv(CHEMIN_VERS_CSV, encoding='cp1252', delimiter=';')
    titre_deja_fait = []
    chemin_fichier_text = CHEMIN_COURANT / "titre_deja_fait" / "titre.txt"

    with open(chemin_fichier_text, 'r') as fichier:
        for ligne in fichier:
            titre_deja_fait.append(ligne.replace("\n",""))

    if titre in titre_deja_fait:
            return "déjà fait"
    else:
        langue = detect_language(text)

        with open(chemin_fichier_text, 'a') as fichier:
                fichier.write(f"\n{titre}")

        titre_n = titre
        titre = titre.replace(" ", "_").replace(":", "_").replace(".", "_").replace("?", "_")
        chemin_fichier = CHEMIN_COURANT/"text"/f"{titre}.txt"
        with open(chemin_fichier, 'w', encoding='utf-8') as file:
            file.write(f"{titre_n}\n")
            file.write(text)

        if langue == "francais":
                resume = resumer_francais(chemin_fichier)
                resume_tr = resume
        else:
                resume = resumer_anglais(chemin_fichier)
                resume_tr = traduction(resume)
            
        with open(CHEMIN_COURANT / "resumer" / f"{titre}.txt", "w", encoding='utf-8') as file:
            file.write(f"{titre_n}\n")
            file.write(resume)
        
        dico = dict()
        date = date_t(date)
        liste_ajout = [titre_n, date, resume, resume_tr, url]
        for y, i in enumerate(df.columns.tolist()):
                dico[i] = liste_ajout[y]
                
                
        df2 = pd.DataFrame([dico])
        df = pd.concat([df, df2])
    df.to_csv(CHEMIN_VERS_CSV, encoding='cp1252', sep=";", index=False)
    return "fait"


def extraire_info_thenextweb():
    """Extrait les infos de thenextweb et les mets dans le csv avec un résumé potentiellement traduit
    """
    page = recuperer_page('https://thenextweb.com/artificial-intelligence')
    liste_url = recuperer_url(page, "o-media xs:o-media--1:1 md:o-media--16:9", "https://thenextweb.com")
    for i in liste_url:
        page = recuperer_page(i)
        date = recuperer_text(page, "time")
        titre = recuperer_text(page, "c-header__heading") 
        text = recuperer_text_plusieur(page, "c-richText c-richText--large")
        print(mettre_csv(titre, date, text, i))
  

    
def extraire_info_actuia():
    """code qui extrait les infos de actuia en utilisant toute les fonctions déjà crée
    """    
    reponse=recuperer_page("https://www.actuia.com/thematique/marche-de-lia/")
    liste_url=recuperer_url(reponse,"td-image-wrap","")
    for i in liste_url:
        page=recuperer_page(i)    
        titre=recuperer_text(page, "entry-title")
        date=recuperer_text(page, "entry-meta")
        text=recuperer_text(page, "entry-content")
        print(mettre_csv(titre, date, text, i))


def trier_csv():
    """Fonction qui trie le csv en fonction des dates"""
    df = pd.read_csv(CHEMIN_VERS_CSV, encoding='cp1252', delimiter=';')
    # Utiliser dayfirst=True pour gérer les formats jour/mois/année
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce', dayfirst=True).combine_first(df['date'])
    df = df.sort_values(by='date', ascending=False)
    df.to_csv(CHEMIN_VERS_CSV, encoding='cp1252', sep=';', index=False)


def trier_csv_scientifique():
    """Fonction qui trie le csv en fonction des dates"""
    df = pd.read_csv(CHEMIN_VERS_CSV_SCIENTIFIQUE, encoding='cp1252', delimiter=';')
    # Utiliser dayfirst=True pour gérer les formats jour/mois/année
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce', dayfirst=True).combine_first(df['date'])
    df = df.sort_values(by='date', ascending=False)
    df.to_csv(CHEMIN_VERS_CSV_SCIENTIFIQUE, encoding='cp1252', sep=';', index=False)


def deep_min():
    """Prends les articles de deep_min et les rajoutes au csv
    """   
    page=recuperer_page("https://deepmind.google/discover/blog/")
    liste_url=recuperer_url(page, "glue-header__link gdm-header__featured-item", "https://deepmind.google")
    for i in liste_url:
        page = recuperer_page(i)
        date = recuperer_text(page, "glue-label gdm-header__featured-date")
        titre = recuperer_text(page, "article-cover__title glue-headline glue-headline--headline-2") 
        text = recuperer_text_plusieur(page, "gdm-rich-text rich-text")
        print(mettre_csv(titre, date, text, i))


def arxiv():
    """Prends les articles scientifique de arxiv et les rajoutes au csv
    """    
    page = recuperer_page("https://arxiv.org/search/advanced?advanced=&terms-0-term=LLM&terms-0-operator=AND&terms-0-field=title&classification-computer_science=y&classification-mathematics=y&classification-physics_archives=all&classification-include_cross_list=include&date-filter_by=past_12&date-year=&date-from_date=&date-to_date=&date-date_type=submitted_date&abstracts=show&size=50&order=-announced_date_first")
    liste_url = recuperer_url_sans_classe(page,"list-title is-inline-block","")
    for href,titre,date in liste_url:
        texte = recuperer_pdf(href)
        
        print(mettre_csv(titre, date, texte, href, CHEMIN_VERS_CSV_SCIENTIFIQUE))


def pipeline_all_site():
    arxiv()
    extraire_info_thenextweb()
    extraire_info_actuia()
    deep_min()
    trier_csv()
    trier_csv_scientifique()


pipeline_all_site()
