Social Media Scheduler

- Add photo
- Ajouter un réseau social Instagram

Commencer à échanger avant toutes ces étapes : 
- Faire fonctionner de multiples connexion à un même Réseaux social pour l'envoie.
- Faire la partie utilisateur
- Commencer la partie analytics
- Voir comment refonctionne le refresh avec le expire_in
- Ajouter un réseau social Pinterest
- Ajouter un réseau social Twitter
- Short URL option
- GIF option

### Update database
cd social-media-scheduler-back\core\models
set FLASK_APP=core.models.db_upgrade.py

ONLY first time -> flask db init

Then -> Each time you want to update db :
flask db migrate

flask db upgrade