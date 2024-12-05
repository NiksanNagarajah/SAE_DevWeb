

import datetime
from .app import mysql
from .app import *

from flask_login import LoginManager, UserMixin

class Cours():
    def __init__(self, coursID, typeC, duree, nbParticipantsMax, jour, heureD, heureF, prix, idM):
        self.coursID = coursID
        self.typeC = typeC
        self.duree = duree
        self.nbParticipantsMax = nbParticipantsMax
        self.jour = jour
        self.heureD = heureD
        self.heureF = heureF
        self.prix = prix
        self.idM = idM

    def __repr__(self):
        return f"Cours({self.coursID}, {self.typeC}, {self.duree}, {self.nbParticipantsMax}, {self.jour}, {self.heureD}, {self.prix}, {self.idM})"

def get_cours():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM COURS ORDER BY jour, heureD")
    les_cours = cursor.fetchall()
    cursor.close()

    class_cours = []
    for cours in les_cours:
        class_cours.append(Cours(cours[0], cours[1], cours[2], cours[3], cours[4], cours[5], cours[6], cours[7], cours[8]))
    
    jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    emploi_du_temps = {jour: [] for jour in jours}
    
    for cours_item in class_cours:
        emploi_du_temps[cours_item.jour].append(cours_item)
    
    start_time = datetime.timedelta(hours=9)  # début à 9h00
    end_time = datetime.timedelta(hours=18)   # fin à 18h00
    
    horaires = []
    current_time = start_time
    
    while current_time < end_time:
        horaires.append(current_time)
        current_time += datetime.timedelta(hours=1)

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT TIME(heureD) FROM COURS")
    test = cursor.fetchall()
    cursor.close()
    print(test)

    return emploi_du_temps, horaires




login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
#Mysql configuration
class Utilisateur(UserMixin):
    def __init__(self, id_membre, nom, prenom, date_naissance, email, mot_de_passe, telephone, poids, niveau, id_trainer, cotisation_annee, cotisation_payee, annee_experience, role):
        self.id_membre = id_membre
        self.nom = nom
        self.prenom = prenom
        self.date_naissance = date_naissance
        self.email = email
        self.mot_de_passe = mot_de_passe
        self.telephone = telephone
        self.poids = poids
        self.niveau = niveau
        self.id_trainer = id_trainer
        self.cotisation_annee = cotisation_annee
        self.cotisation_payee = cotisation_payee
        self.annee_experience = annee_experience
        self.role = role
    def get_id(self):
        return str(self.id_membre)

@login_manager.user_loader
def load_user(idM):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM MEMBRE WHERE idM = %s", (idM,))
    user_data = cursor.fetchone()
    cursor.close() #peut être remplacer par une fonction
    print(user_data, "c'est le user_data")

    if user_data:
        return Utilisateur(*user_data)
    return None



def get_email_membre(email):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT email FROM MEMBRE WHERE email = %s", (email,))
    existing_user = cursor.fetchone()
    cursor.close()
    return existing_user


def get_all_user_info(email):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM MEMBRE WHERE email = %s", (email,))
    user_data = cursor.fetchone()
    cursor.close()

    if user_data:
        return Utilisateur(*user_data)  
    return None


def get_motdepasse(email):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT motDePasse FROM MEMBRE WHERE email = %s", (email,))
    motdepasse = cursor.fetchone()
    cursor.close()
    return motdepasse[0] if motdepasse else None


def insert_membre(nomM, prenomM, dateNaissance, email, motDePasse, telephone, poidsA, niveau, idT):
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO MEMBRE (nomM, prenomM, dateNaissance, email, motDePasse, telephone, poidsA, niveau, idT) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (nomM, prenomM, dateNaissance, email, motDePasse, telephone, poidsA, niveau, idT))
    mysql.connection.commit()
    cursor.close()


def cours_reserves(user_id):
    """Récupère les cours réservés par un utilisateur spécifique et les retourne sous forme d'objets Cours.

    Args:
        user_id (int): L'identifiant de l'utilisateur.

    Returns:
        list[Cours]: Liste des objets Cours correspondant aux réservations de l'utilisateur.
    """
    try:
        cursor = mysql.connection.cursor()
        query = """
            SELECT c.coursID, c.typeC, c.duree, c.nbParticipantsMax, c.jour, 
                   c.heureD, c.heureF, c.prix, c.idM
            FROM RESERVATION r
            JOIN COURS c ON r.coursID = c.coursID
            WHERE r.idM = %s
        """
        cursor.execute(query, (user_id,))
        cours_reserves_raw = cursor.fetchall()
        cursor.close()

        # Convertir les données brutes en objets Cours
        cours_reserves = [
            Cours(
                coursID=c[0],
                typeC=c[1],
                duree=c[2],
                nbParticipantsMax=c[3],
                jour=c[4],
                heureD=c[5],
                heureF=c[6],
                prix=c[7],
                idM=c[8]
            )
            for c in cours_reserves_raw
        ]

    except Exception as e:
        print(f"Erreur lors de la récupération des cours : {e}")
        cours_reserves = []

    return cours_reserves


def profil_utilisateur(user_id):
    try:
        cursor = mysql.connection.cursor()
        query = """
            SELECT idM, nomM, prenomM, dateNaissance, email, motDePasse, telephone, poidsA, niveau, idT, cotisationAnnee, cotisationPayee, anneeExperience, roleM
            FROM MEMBRE
            WHERE idM = %s
        """
        cursor.execute(query, (user_id,))
        profil = cursor.fetchall()
        cursor.close()
        # Convertir les données brutes en objets Cours
        profil_ = [
            Utilisateur(
                id_membre=p[0],
                nom=p[1],
                prenom=p[2],
                date_naissance=p[3],
                email=p[4],
                mot_de_passe=p[5],
                telephone=p[6],
                poids=p[7],
                niveau=p[8],
                id_trainer=p[9],
                cotisation_annee=p[10],
                cotisation_payee=p[11],
                annee_experience=p[12],
                role=p[13]
                
            )
            for p in profil
        ]

    except Exception as e:
        print(f"Erreur lors de la récupération du profil : {e}")
        profil_ = []

    return profil_
  
class Tarif():
    def __init__(self, idT, description, ageMin, ageMax, prix):
        self.idT = idT
        self.description = description
        self.ageMin = ageMin
        self.ageMax = ageMax
        self.prix = prix

    def __repr__(self):
        return f"Tarif({self.idT}, {self.description}, {self.ageMin}, {self.ageMax}, {self.prix})"

def getIdTarif(dateNaissance):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM TARIF")
    tarifs = cursor.fetchall()
    cursor.close()

    lesTarifs = []
    for tarif in tarifs:
        lesTarifs.append(Tarif(tarif[0], tarif[1], tarif[2], tarif[3], tarif[4]))        
    age = datetime.datetime.now().year - dateNaissance.year
    for tarif in lesTarifs:
        if tarif.ageMin <= age <= tarif.ageMax:
            return tarif.idT
    return 1

