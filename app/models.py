

import datetime
from .app import mysql


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

# les_cours = (
#     (1, 'Collectif', 1, 10, 'Lundi', datetime.timedelta(seconds=32400), datetime.timedelta(seconds=36000), Decimal('20.00'), 4), 
#     (11, 'Collectif', 1, 10, 'Lundi', datetime.timedelta(seconds=34200), datetime.timedelta(seconds=37800), Decimal('20.00'), 6), 
#     (6, 'Collectif', 1, 5, 'Lundi', datetime.timedelta(seconds=36000), datetime.timedelta(seconds=39600), Decimal('15.00'), 4), 
#     (7, 'Collectif', 2, 8, 'Mardi', datetime.timedelta(seconds=50400), datetime.timedelta(seconds=57600), Decimal('35.00'), 4), 
#     (2, 'Collectif', 2, 1, 'Mercredi', datetime.timedelta(seconds=50400), datetime.timedelta(seconds=57600), Decimal('30.00'), 4), 
#     (8, 'Particulier', 1, 1, 'Mercredi', datetime.timedelta(seconds=57600), datetime.timedelta(seconds=61200), Decimal('45.00'), 4), 
#     (9, 'Collectif', 1, 6, 'Jeudi', datetime.timedelta(seconds=46800), datetime.timedelta(seconds=50400), Decimal('20.00'), 4), 
#     (3, 'Particulier', 1, 1, 'Vendredi', datetime.timedelta(seconds=39600), datetime.timedelta(seconds=43200), Decimal('25.00'), 4), 
#     (10, 'Particulier', 2, 1, 'Vendredi', datetime.timedelta(seconds=55800), datetime.timedelta(seconds=63000), Decimal('50.00'), 4), 
#     (4, 'Collectif', 1, 10, 'Samedi', datetime.timedelta(seconds=36000), datetime.timedelta(seconds=39600), Decimal('20.00'), 4), 
#     (5, 'Particulier', 2, 1, 'Samedi', datetime.timedelta(seconds=39600), datetime.timedelta(seconds=46800), Decimal('40.00'), 4)
# )

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
