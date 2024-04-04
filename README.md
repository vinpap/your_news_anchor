# your_news_anchor
Le code présent dans ce dépôt permet d'extraire le contenu d'articles de journaux listés dans des flux RSS et de l'enregistrer dans une base de données via [l'API de 'Your News Anchor'](https://github.com/vinpap/your_news_anchor_db_api). Il fonctionne en quatre étapes :
- dans un premier temps, le script interroge la base de données via l'API pour récupérer la liste de toutes les sources d'information enregistrées
- ensuite, il parcourt les flux RSS de chaque source pour en extraire une liste d'URLs d'articles à traiter
- le script extrait le contenu de chaque article ainsi que d'autres informations le concernant (date de publication, auteurs...)
- enfin, le contenu des articles est stocké dans la base de données en repassant par l'API. Les articles qui y étaient précédemment enregistrés sont supprimés.

## Lancer l'extraction des articles

Le script **extract_articles.py** permet d'extraire le contenu des articles. Voici les étapes nécessaires à son exécution :
1) Installer les dépendances :
```
pip install -r requirements.txt
python -m spacy download fr_core_news_lg
```
2) Définir les variables d'environnement : pour utiliser ce code il faut définir l'URL et la clé de sécurité de l'API qui permet d'accéder à la base de données où sont stockés les flux RSS à utiliser et les articles déjà extraits :
```
export "API"="vincent-your-news-anchor.azurewebsites.net"
export "API_TOKEN"="<entrez la clé de l'API ici>"
```
Notez que ces valeurs doivent être à nouveau définies si l'API est redéployée ailleurs. 
3) Exécuter le script :
```
python extract_articles.py
```
**Remarque :** ce script est destiné à être exécuté toutes les 24 heures pour que les articles enregistrés dans la base de données soient toujours d'actualité. [PythonAnywhere](https://www.pythonanywhere.com/) a été utilisé pour automatiser l'exécution du script, mais d'autres solutions telles qu'[Azure Functions](https://azure.microsoft.com/fr-fr/products/functions).

## Tester le code
Des tests unitaires sont disponibles dans le dossier 'test' pour vérifier le fonctionnement des fonctions d'extraction de contenu. Ces tests sont exécutés automatiquement grâce à GitHub Actions lorsque du nouveau code est poussé sur GitHub, mais il est aussi possible de les exécuter manuellement :
```
pip install -r requirements.txt
python -m spacy download fr_core_news_lg
pytest
```
