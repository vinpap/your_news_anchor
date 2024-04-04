# your_news_anchor
Le code présent dans ce dépôt permet d'extraire le contenu d'articles de journaux listés dans des flux RSS et de l'enregistrer dans une base de données via [l'API de 'Your News Anchor'](https://github.com/vinpap/your_news_anchor_db_api).

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
export "API_KEY"="<entrez la clé de l'API ici>"
```
Notez que ces valeurs doivent être à nouveau définies si l'API est redéployée ailleurs. 
3) Exécuter le script :
```
python extract_articles.py
```
## Tester le code
Penser à détailler un peu les tests
