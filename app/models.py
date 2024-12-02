

import datetime
from .app import *

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

les_cours = [
    (1, 'Collectif', 1, 10, 'Lundi', datetime.time(9, 0), datetime.time(10, 0), 20.0, 4),
    (6, 'Collectif', 1, 5, 'Lundi', datetime.time(10, 0), datetime.time(11, 0), 15.0, 4),
    (7, 'Collectif', 2, 8, 'Mardi', datetime.time(14, 0), datetime.time(16, 0), 35.0, 4),
    (2, 'Collectif', 2, 1, 'Mercredi', datetime.time(14, 0), datetime.time(16, 0), 30.0, 4),
    (8, 'Particulier', 1, 1, 'Mercredi', datetime.time(16, 0), datetime.time(17, 0), 45.0, 4),
    (9, 'Collectif', 1, 6, 'Jeudi', datetime.time(13, 0), datetime.time(14, 0), 20.0, 4),
    (3, 'Particulier', 1, 1, 'Vendredi', datetime.time(11, 0), datetime.time(12, 0), 25.0, 4),
    (10, 'Particulier', 2, 1, 'Vendredi', datetime.time(15, 30), datetime.time(17, 30), 50.0, 4),
    (5, 'Particulier', 2, 1, 'Samedi', datetime.time(11, 0), datetime.time(13, 0), 40.0, 4),
    (4, 'Collectif', 1, 10, 'Samedi', datetime.time(10, 0), datetime.time(11, 0), 20.0, 4)
]

def get_cours():
    # Il faut trier les cours par jour et heureD
    class_cours = []
    for cours in les_cours:
        class_cours.append(Cours(cours[0], cours[1], cours[2], cours[3], cours[4], cours[5], cours[6], cours[7], cours[8]))
        print(Cours(cours[0], cours[1], cours[2], cours[3], cours[4], cours[5], cours[6], cours[7], cours[8]))
    
    jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    emploi_du_temps = {jour: [] for jour in jours}
    
    # Remplir le dictionnaire avec les cours
    for cours_item in class_cours:
        # print(cours_item)
        emploi_du_temps[cours_item.jour].append(cours_item)
    
    horaires = []
    start_time = datetime.time(9, 0)  # début à 9h00
    end_time = datetime.time(18, 0)   # fin à 18h00
    
    # Créer une liste de créneaux horaires
    current_time = start_time
    while current_time < end_time:
        horaires.append(current_time)
        # Ajouter une heure au créneau
        current_time = (datetime.datetime.combine(datetime.date.today(), current_time) + datetime.timedelta(hours=1)).time()

    return emploi_du_temps, horaires

def cours_reserves(user_id):
    try:
        cursor = mysql.connection.cursor()
        query = """
            SELECT c.typeC, c.jour, c.heureD, c.heureF, c.prix
            FROM RESERVATION r
            JOIN COURS c ON r.coursID = c.coursID
            WHERE r.idM = %s
        """
        cursor.execute(query, (user_id,))
        cours_reserves = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print(f"Erreur lors de la récupération des cours : {e}")
        cours_reserves = []
    return cours_reserves