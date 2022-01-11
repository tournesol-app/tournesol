# Généralités

Tournesol est un projet open source provenant de l’association du même nom. Tournesol cherche à résoudre le problème urgent de l’éthique des intelligence artificielle, des biais algorithmiques dans la recommandation de contenu en ligne et de la mésinformation. Son but est de créer une plateforme qui permet d’identifier les vidéo Youtube de grande qualité afin de les recommander. Les visiteurs du site peuvent librement consulter les recommandations de Tournesol et utiliser les différents filtres pour affiner leur recherche.

Pour être proactif dans le processus de recommandation, les utilisateurs peuvent se créer un compte et comparer des vidéos deux par deux selon différents critères. Ces comparaisons sont agrégées par un algorithme de Machine Learning développé par des chercheurs de l’EPFL et encadrés par le président de l’association.

En termes de personnes travaillant sur le projet, il y a les membres du bureau, travaillant sur leur temps libre (Lé, Louis, Aidan) et deux employés à plein temps, développeur [Adrien][Adrien] et [Romain][Romain].

Le projet est open source, toute personne peut contribuer comme elle peut. On peut noter l’implication de [Julien](https://github.com/jstainer-kleis) qui travaille pour KLEIS et s’est occupé du déploiement de l’infra.
Concernant la partie ML, ce sont des chercheurs de l’EPFL qui s'occupent de développer les algorithmes.


#  Architecture

## Backend

Le backend de l’application est codé en Python avec Django. Beaucoup de vues sont développés avec le framework [django-rest-framework](https://www.django-rest-framework.org/)

Deux grandes applications constituent le corps du back: core et tournesol :
- L’app `core` réfère à tout ce qui concerne les utilisateurs de l’application. On y retrouve donc dedans les modèles `User` et aussi le nécessaire pour vérifier les adresses avec les noms de domaines vérifiées `EmailDomain` et `Verifiable Email`

- Le cœur du back est contenu dans l’app `tournesol`. On retrouve donc les 3 grands éléments permettant de noter des vidéos :
    - On a tout d’abord un modèle `Video` qui est réutilisé pour savoir son score pour chaque vidéo dans `VideoCriteriaScore`. Un modèle `VideoRateLater` pointe aussi sur une vidéo à noter plus tard par un utilisateur donné.
    - Vient ensuite la catégorie comparaison avec le modèle `Comparison` qui enregistre une comparaison faite par un utilisateur entre 2 vidéos distinctes. Et par la suite `ComparisonCriteriaScore` qui vient détailler le score de chaque critère pour une comparaison donnée.
    - Enfin, le modèle `ContributorRating` contient la notation des vidéos que chaque personne a comparé, en sortie de l’algorithme. On y retrouve aussi le modèle associé qui contient le score associé à chaque critère pour un rating donné.

Tous les modèles présentent un ou plusieurs serializers en fonction de vues de l’API. On utilise les classes de Base de Rest Framework pour automatiser la reconnaissance des paramètres pour l’utilisation d’ OpenApi.

Enfin on retrouve les vues qui sont les fonctions activées à partir de chacune des urls. Là encore on utilise beaucoup de Classes et de Mixin de Rest Framework pour aider à l’utilisation d’OpenApi.

Lors de la modification ou de la création de nouvelles vues, il est important de bien mettre à jour les descriptions et paramètres des vues pour qu’ OpenApi prenne bien en compte les changements.

##  OpenApi

Documentation: https://www.openapis.org/

L’utilisation d’OpenApi facilite grandement le développement de l’application entre React et Django. Python est un langage qui ne possède pas de typage. Chaque variable peut recevoir le type qu’elle veut et en changer en cours d’exécution de fonction par exemple. En revanche côté React utilisé avec Typescript, chaque constante ou variable instanciée doit l’être avec un type donné.

Côté Back, l’utilisation d’OpenApi est présente pour :
- les serializers, au travers de Rest Framework
- les vues, au travers de Rest Framework et de la documentation du schéma

Coté Front, on récupère :
- dans `scripts` : le schéma de l’API dans un yaml avec un fichier shell pour mettre à jour les types à partir du yaml
- `src/services` : la génération automatique des différents types pour les différents serializers et les vues (en parle plutôt d’endpoint du point de vue Front) de l’API

## Frontend

Le frontend est développé en Typescript et utilise principalement les librairies React et [Material-UI](https://mui.com/getting-started/usage/).

Le répertoire `public` recense tous les fichiers statiques de l’application (css, image, l’index html public)

Pour la partie `script`, se référer à la section précédente.

La partie centrale du front se situe dans `src`:
- `components` : contient tous les components génériques de l’application qui servent de cadrage pour avoir un site cohérent en termes de styles (loader, titre de page, box, etc…)
- `utils`: contient tout type de constantes, de logiques métiers, fonctions pouvant être réutilisées à plusieurs endroits de l’application.
- `pages`: contient la première couche de component qui est directement appelé après le routeur de l’application
- `features` : contient les components propres à chacune des pages de l’application. Le rangement est presque partout cohérent avec leur utilité et les pages associées.
- `hooks`: permet de rajouter des hooks customisés pour l’application.

Le fichier contenant le routing de l’application (association entre url du navigateur et component à loader) se situe dans `App.tsx`.

Les bases du thème (css) se situe dans `theme.css`.

Toutes les pages de feature sont basées sur le même modèle. Tout d’abord, il y a les imports, puis les classes css propres au component qu’on met au maximum dans `sx` puis les hooks du component, et enfin le render.

# Les choses utiles

## Installation

### Back

- Cloner le projet
- Lancer une image de docker postgres
- Suivre la [doc du back](https://github.com/tournesol-app/tournesol/tree/main/backend)
- Installer les dépendances de test dans les dossier `tests`
- Faire le Setup d’une clé API pour discuter avec l’API Youtube

### Front

- Installer nvm 
- Installer la version 14 `nvm install 14` et puis ` npm install -global yarn`
- Créer un envrionement virtuel `mkvirtualenv {nom}`
- Suivre la section Installation du front

## Tips

- Pour le backend, quand une modification est faite, il faut (toujours) écrire un test ou préciser un test existant. La commande `pytest` permet de lancer tous les tests.
Cependant la commande `pytest --html=report.html –self-contained-html` permet de créer un fichier de rapport propre avec le détail du log séparé pour chacun des tests.

- Pour mettre à jour le schéma d’OpenApi et plus précisément le `.yaml`, il faut d’abord lancer le back, puis dans le dossier du front tapez la commande `yarn run update-schema`.

- Pour mettre à jour les fichiers dépendant du .yaml d’OpenApi, il faut lancer la commande suivante le dossier `scripts` du front : ` ./generate-services-from-openapi.sh`.

- Pour corriger le style du code de manière automatique, il est possible d’activer un plugin selon l’IDE. Sinon on la commande `yarn lint:fix` permet dans tous les cas de corriger le code de manière automatique.

# Fonctionnement de MR/projet

Le suivi du projet et des tâches en cours se fait sur ce [board](https://github.com/tournesol-app/tournesol/projects/9)

Il est possible de créer des idées qui nous semblent pertinentes en éditant une issue et en la plaçant dans la colonne `Backlog and ideas`.

La core-team décide par la suite des tâches à prioriser et dépose les tickets correspondants dans la colonne `Ready`. On peut s’assigner sur un ticket après avoir discuté avec [Adrien][Adrien], [Romain][Romain]. ou [Louis][Louis].

Quand votre travail est assez avancé vous pouvez créer une PR de votre branche vers `main` sous Github. Vous pouvez aussi demander à [Adrien][Adrien] ou [Romain][Romain] de relire votre PR mais si non totalement aboutie (PR en statut draft) pour avoir quelques feedbacks et potentiellement modifier certaines choses.

Quand votre PR vous semble dans un bon état pour être mergé, demandez la revue d’[Adrien][Adrien], [Romain][Romain] et [Louis][Louis] (au moins). L’opération de merge ne peut être effectuée que si au moins une personne approuve votre PR.

Un changement dans le back doit impliquer des tests pour contrôler le comportement attendu, ainsi que les possibles comportements qui doivent être évités.

Côté front, une modification peut aussi s’accompagner de tests pour le component dédié.

La création de test end-to-end n’est pas systématique et il est bon de voir avec [Adrien][Adrien] et [Romain][Romain] pour savoir l’utilité d’un nouveau test.

Pour se tenir au courant des avancées du projet, des bugs, rejoignez le [discord][tournesol-discord-join]

[tournesol-discord-join]: https://discord.gg/WvcSG55Bf3
[Adrien]: https://github.com/amatissart
[Romain]: https://github.com/GresilleSiffle
[Louis]: https://github.com/lfaucon