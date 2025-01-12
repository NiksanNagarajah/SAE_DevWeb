

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
        return f"Cours {self.typeC} le {self.jour} de {self.heureD} à {self.heureF} pour {self.prix}€"

def get_cours(idM=None):
    cursor = mysql.connection.cursor()
    if idM:
        cursor.execute("SELECT * FROM COURS WHERE idM = %s ORDER BY jour, heureD", (idM,))
    else:
        cursor.execute("SELECT * FROM COURS ORDER BY jour, heureD")
    les_cours = cursor.fetchall()
    cursor.close()

    class_cours = []
    for cours in les_cours:
        class_cours.append(Cours(cours[0], cours[1], cours[2], cours[3], cours[4], cours[5], cours[6], cours[7], cours[8]))

    # Convertir les données pour FullCalendar
    events = []
    # Obtenir la date d'aujord'hui
    today = datetime.datetime.now().date()
    lundi = today - datetime.timedelta(days=today.weekday())
    jours_mapping = {
        'Lundi': lundi, 
        'Mardi': lundi + datetime.timedelta(days=1),
        'Mercredi': lundi + datetime.timedelta(days=2),
        'Jeudi': lundi + datetime.timedelta(days=3),
        'Vendredi': lundi + datetime.timedelta(days=4),
        'Samedi': lundi + datetime.timedelta(days=5),
        'Dimanche': lundi + datetime.timedelta(days=6),
    }

    for cours_item in class_cours:
        if len(str(cours_item.heureD)) == 7:
            cours_item.heureD = "0" + str(cours_item.heureD)
        if len(str(cours_item.heureF)) == 7:
            cours_item.heureF = "0" + str(cours_item.heureF)
        start_time = f"{jours_mapping[cours_item.jour]}T{cours_item.heureD}"
        end_time = f"{jours_mapping[cours_item.jour]}T{cours_item.heureF}"
        nom_Moniteur = get_monitor_name(cours_item.idM)
        events.append({
            "title": f"{cours_item.typeC} - {cours_item.nbParticipantsMax} participants Max - {nom_Moniteur[0]} {nom_Moniteur[1]} - {cours_item.prix}€",
            "start": start_time,
            "end": end_time,
        })

    return events




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
    
    def is_admin(self):
        return self.role == 'Administrateur'
    
    def is_monitor(self):
        return self.role == 'Moniteur'
    
    def is_adherent(self):
        return self.role == 'Adhérent'
    
    def __repr__(self):
        return f"{self.nom} {self.prenom}"

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


def insert_membre(nomM, prenomM, dateNaissance, email, motDePasse, telephone, poidsA, niveau, idT, roleM="Adhérent"):
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO MEMBRE (nomM, prenomM, dateNaissance, email, motDePasse, telephone, poidsA, niveau, idT, roleM) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (nomM, prenomM, dateNaissance, email, motDePasse, telephone, poidsA, niveau, idT, roleM))
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

def get_monitor_name(idM):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT nomM, prenomM FROM MEMBRE WHERE idM = %s", (idM,))
    monitor_name = cursor.fetchone()
    cursor.close()
    return monitor_name


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

class Poney():
    def __init__(self, poneyID, nomP, age, poidsSupportableMax):
        self.poneyID = poneyID
        self.nomP = nomP
        self.age = age
        self.poidsSupportableMax = poidsSupportableMax

    def __repr__(self):
        return f"{self.nomP} : {self.age} ans"

def getPoneys():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM PONEY")
    poneys = cursor.fetchall()
    cursor.close()

    lesPoneys = []
    for poney in poneys:
        lesPoneys.append(Poney(poney[0], poney[1], poney[2], poney[3]))        
    return lesPoneys

def modifierPoney(nomP, age, poidsSupportableMax, poneyID):
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE PONEY SET nomP = %s, age = %s, poidsSupportableMax = %s WHERE poneyID = %s", (nomP, age, poidsSupportableMax, poneyID))
    mysql.connection.commit()
    cursor.close()

def supprimerPoney(poneyID):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM PONEY WHERE poneyID = %s", (poneyID,))
    mysql.connection.commit()
    cursor.close()

def ajouterPoney(nomP, age, poidsSupportableMax):
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO PONEY (nomP, age, poidsSupportableMax) VALUES (%s, %s, %s)", (nomP, age, poidsSupportableMax))
    mysql.connection.commit()
    cursor.close()

def getPoney(poney_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM PONEY WHERE poneyID = %s", (poney_id,))
    poney = cursor.fetchone()
    cursor.close()
    return Poney(poney[0], poney[1], poney[2], poney[3]) 


class Reservation():
    def __init__(self, idM, poneyID, coursID, coursPayee=True):
        self.idM = idM
        self.poneyID = poneyID
        self.coursID = coursID
        self.coursPayee = coursPayee
    
    def __repr__(self):
        return f"Reservation({self.idM}, {self.coursID}, {self.coursPayee})"


def getPoneyForRerservation(poidsAdherent):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM PONEY WHERE poidsSupportableMax >= %s", (poidsAdherent,))
    reservations = cursor.fetchall()
    cursor.close()

    lesPoneys = []
    for poney in reservations:
        lesPoneys.append((poney[0], Poney(poney[0], poney[1], poney[2], poney[3])))
    return lesPoneys

def getCoursForReservation(idM):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM COURS WHERE coursID NOT IN (SELECT coursID FROM RESERVATION WHERE idM=%s) ORDER BY jour, heureD", (idM,))
    cours = cursor.fetchall()
    cursor.close()

    lesCours = []
    for cour in cours:
        lesCours.append((cour[0], Cours(cour[0], cour[1], cour[2], cour[3], cour[4], cour[5], cour[6], cour[7], cour[8])))
    return lesCours

def ajouterReservation(idM, poneyID, coursID):
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO RESERVATION (idM, poneyID, coursID, coursPayee) VALUES (%s, %s, %s, true)", (idM, poneyID, coursID))
    mysql.connection.commit()
    cursor.close()    

def get_membres(role, idM):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM MEMBRE WHERE roleM = %s and idM != %s", (role, idM,))
    membres = cursor.fetchall()
    cursor.close()

    lesMembres = []
    for membre in membres:
        lesMembres.append(Utilisateur(membre[0], membre[1], membre[2], membre[3], membre[4], membre[5], membre[6], membre[7], membre[8], membre[9], membre[10], membre[11], membre[12], membre[13]))
    return lesMembres

def changerRole(idM, role):
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE MEMBRE SET roleM = %s WHERE idM = %s", (role, idM))
    mysql.connection.commit()
    cursor.close()

def supprimerReservationDuMembre(idM):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM RESERVATION WHERE idM = %s", (idM,))
    mysql.connection.commit()
    cursor.close()

def supprimerCoursDuMembre(idM):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM COURS WHERE idM = %s", (idM,))
    mysql.connection.commit()
    cursor.close()

def supprimerReservationDuCours(coursID):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM RESERVATION WHERE coursID = %s", (coursID,))
    mysql.connection.commit()
    cursor.close()

def getCoursSimple():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM COURS ORDER BY jour, heureD")
    cours = cursor.fetchall()
    cursor.close()

    lesCours = []
    for cour in cours:
        lesCours.append(Cours(cour[0], cour[1], cour[2], cour[3], cour[4], cour[5], cour[6], cour[7], get_monitor_name(cour[8])))
    return lesCours

def ajouterCours(typeC, duree, nbParticipantsMax, jour, heureD, prix, idM):
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO COURS (typeC, duree, nbParticipantsMax, jour, heureD, prix, idM) VALUES (%s, %s, %s, %s, %s, %s, %s)", (typeC, duree, nbParticipantsMax, jour, heureD, prix, idM))
    mysql.connection.commit()
    cursor.close()

def supprimerCours(coursID):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM COURS WHERE coursID = %s", (coursID,))
    mysql.connection.commit()
    cursor.close()

def modifierCours(typeC, duree, nbParticipantsMax, jour, heureD, heureF, prix, idM, coursID):
    print(typeC, duree, nbParticipantsMax, jour, heureD, heureF, prix, idM, coursID)
    cursor = mysql.connection.cursor()
    print(typeC, duree, nbParticipantsMax, jour, heureD, heureF, prix, idM, coursID)
    cursor.execute("UPDATE COURS SET typeC = %s, duree = %s, nbParticipantsMax = %s, jour = %s, heureD = %s, heureF = %s, prix = %s, idM = %s WHERE coursID = %s", (typeC, duree, nbParticipantsMax, jour, heureD, heureF, prix, idM, coursID))
    print(typeC, duree, nbParticipantsMax, jour, heureD, heureF, prix, idM, coursID)
    mysql.connection.commit()
    print(typeC, duree, nbParticipantsMax, jour, heureD, heureF, prix, idM, coursID)
    cursor.close()
    print(typeC, duree, nbParticipantsMax, jour, heureD, heureF, prix, idM, coursID)

# Modifier Cours ???

# def modifierCours(typeC, duree, nbParticipantsMax, jour, heureD, prix, coursID):
#     cursor = mysql.connection.cursor()
#     cursor.execute("UPDATE COURS SET typeC = %s, duree = %s, nbParticipantsMax = %s, jour = %s, heureD = %s, prix = %s WHERE coursID = %s", (typeC, duree, nbParticipantsMax, jour, heureD, prix, coursID))
#     mysql.connection.commit()
#     cursor.close()

def getMoniteursForCours(idM=None):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM MEMBRE WHERE roleM = 'Moniteur'")
    moniteurs = cursor.fetchall()
    cursor.close()

    lesMoniteurs = []
    for moniteur in moniteurs:
        if idM and moniteur[0] == idM:
            moniteurCourant = (moniteur[0], Utilisateur(moniteur[0], moniteur[1], moniteur[2], moniteur[3], moniteur[4], moniteur[5], moniteur[6], moniteur[7], moniteur[8], moniteur[9], moniteur[10], moniteur[11], moniteur[12], moniteur[13]))
        lesMoniteurs.append((moniteur[0], Utilisateur(moniteur[0], moniteur[1], moniteur[2], moniteur[3], moniteur[4], moniteur[5], moniteur[6], moniteur[7], moniteur[8], moniteur[9], moniteur[10], moniteur[11], moniteur[12], moniteur[13])))
    if idM:
        lesMoniteurs.insert(0, moniteurCourant)
    return lesMoniteurs

def getCours(coursID):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM COURS WHERE coursID = %s", (coursID,))
    cours = cursor.fetchone()
    cursor.close()
    return Cours(cours[0], cours[1], cours[2], cours[3], cours[4], cours[5], cours[6], cours[7], cours[8])

def moniteurACours(coursID, jour, heureD, heureF, idM):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM COURS WHERE coursID != %s and idM = %s AND jour = %s AND ((heureD < %s AND heureF > %s) OR (heureD < %s AND heureF > %s) OR (heureD >= %s AND heureF <= %s))", (coursID, idM, jour, heureD, heureD, heureF, heureF, heureD, heureF))
    cours = cursor.fetchall()
    cursor.close()
    print(cours)
    if len(cours) > 0:
        return True
    return False

    