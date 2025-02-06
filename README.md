# tradingview-flask-app
A little app designed to catch webhooks post requests from Trading view

Source : 
* Part Time Larry :  https://www.youtube.com/watch?v=gMRee2srpe8


## Langage de programation
Installer le langage [Python](https://www.python.org/downloads/)

## Editeur de texte
Installer l'éditeur [Visual studio](https://code.visualstudio.com/) 

Install pip package for vs studio extensions : 
```
pip install autopep8 
pip install pylint
```

Install VS Code extensions : 
- Python/Pylance
- PowerShell
- Markdown Preview Enhancer

## Github
Pour chaque nouveau projet créer un répertoire directement depuis le [GitHub](https://github.com/)
### Les commandes à connaitre 
Pour cloner un répertoire existant depuis github : 
```
git clone <url>
```
Pour afficher la liste des fichiers/dossiers modifiés : 
```
git status
```
Pour ajouter des fichiers/dossiers non inclus : 
```
git add <fichier/dossier>
git add .
```
Pour créer un commit : 
```
git commit -m “description du commit”
```
Pour uploader les modifications sur github (sur la branche master) : 
```
git push origin master
```
Pour extraire mettre à jour le dossier depuis githup : 
```
git fetch origin
```
Pour fusionner depuis github : 
```
git pull
```
Pour lister les commits (taper q pour quitter) : 
```
git log 
```

### Le fichier ".gitignore"
Il est créé à la racine du projet pour indiquer les fichier à ne pas upload sur le répertoire github en ligne, à inclure (pour un projet Django):

## Environnement virtuel
Installer le package d’environnement virtuel : 
```
pip install virtualenv
```
Creer l’environnement virtuel : 
```
python -m venv <virtual-environnement-name>
```
Activer l’environnement virtuel : 
- Linux/Mac :
```
source <virtual-environnement-name>/bin/activate
```
- Windows :
```
Set-ExecutionPolicy Unrestricted -Scope Process (si fontionne pas)
env\Scripts\activate
```
Désactiver l’environnement virtuel :
``` 
deactivate
```

## Installer les Packages : 
```
pip install <some-dependance>
```
Lister les dépendances : 
```
pip freeze
```
Ajouter les dépendances à un fichier “requirement.txt”
```
pip freeze > requirement.txt
```
Installer les dépendances présentes dans un fichier “requirement.txt” : 
```
pip install -r requirement.txt
```

## Flask App : 

Installer flask
```
pip install flask
```

First create a simple app "app.py" returning "Hello World" localy.
-->  Attention, ne pas laisser debug=True en production. 

To run app.py
```
python3 app.py
```
Write some html templates with inheritence and redirection.
Create static file for image and css
Set bootstrap and make a base page using jinja syntax.


--> Deal with POST REQUEST