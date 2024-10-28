INSERT INTO TARIF (descriptif, montant) VALUES ('Tarif enfant', 20.00);
INSERT INTO TARIF (descriptif, montant) VALUES ('Tarif adulte', 30.00);
INSERT INTO TARIF (descriptif, montant) VALUES ('Tarif étudiant', 25.00);
INSERT INTO TARIF (descriptif, montant) VALUES ('Tarif senior', 22.00);
INSERT INTO TARIF (descriptif, montant) VALUES ('Tarif membre', 18.00);


INSERT INTO MEMBRE (nomM, prenomM, dateNaissance, email, motDePasse, telephone, poidsA, niveau, idT, cotisationAnnee, cotisationPayee, roleM)
VALUES ('Dupont', 'Jean', '1985-03-12', 'jean.dupont@example.com', 'password123', '0612345678', 65.0, 'Intermédiaire', 2, 2023, TRUE, 'Adhérent');

INSERT INTO MEMBRE (nomM, prenomM, dateNaissance, email, motDePasse, telephone, poidsA, niveau, idT, cotisationAnnee, cotisationPayee, roleM)
VALUES ('Martin', 'Sophie', '1990-07-25', 'sophie.martin@example.com', 'password123', '0612345679', 55.0, 'Débutant', 1, 2023, TRUE, 'Adhérent');

INSERT INTO MEMBRE (nomM, prenomM, dateNaissance, email, motDePasse, telephone, poidsA, niveau, idT, cotisationAnnee, cotisationPayee, roleM)
VALUES ('Leroy', 'Emma', '2000-10-30', 'emma.leroy@example.com', 'password123', '0612345680', 65.0, 'Avancé', 3, 2023, FALSE, 'Adhérent');

INSERT INTO MEMBRE (nomM, prenomM, dateNaissance, email, motDePasse, telephone, anneeExperience, roleM)
VALUES ('Bernard', 'Paul', '1975-05-15', 'paul.bernard@example.com', 'password123', '0612345681', 6, 'Moniteur');

INSERT INTO MEMBRE (nomM, prenomM, dateNaissance, email, motDePasse, telephone, anneeExperience, roleM)
VALUES ('Renard', 'Alice', '1988-11-22', 'alice.renard@example.com', 'password123', '0612345682', 1, 'Administrateur');


INSERT INTO COURS (typeC, duree, nbParticipantsMax, jour, heureD, prix, idM) VALUES ('Collectif', 1, 10, 'Lundi', '09:00:00', 20.00, 4);
INSERT INTO COURS (typeC, duree, nbParticipantsMax, jour, heureD, prix, idM) VALUES ('Collectif', 2, 1, 'Mercredi', '14:00:00', 30.00, 4);
INSERT INTO COURS (typeC, duree, nbParticipantsMax, jour, heureD, prix, idM) VALUES ('Particulier', 1, 1, 'Vendredi', '11:00:00', 25.00, 4);
INSERT INTO COURS (typeC, duree, nbParticipantsMax, jour, heureD, prix, idM) VALUES ('Collectif', 1, 10, 'Samedi', '10:00:00', 20.00, 4);
INSERT INTO COURS (typeC, duree, nbParticipantsMax, jour, heureD, prix, idM) VALUES ('Particulier', 2, 1, 'Samedi', '11:00:00', 40.00, 4);
INSERT INTO COURS (typeC, duree, nbParticipantsMax, jour, heureD, prix, idM) VALUES ('Collectif', 1, 5, 'Lundi', '10:00:00', 15.00, 4);
INSERT INTO COURS (typeC, duree, nbParticipantsMax, jour, heureD, prix, idM) VALUES ('Collectif', 2, 8, 'Mardi', '14:00:00', 35.00, 4);
INSERT INTO COURS (typeC, duree, nbParticipantsMax, jour, heureD, prix, idM) VALUES ('Particulier', 1, 1, 'Mercredi', '16:00:00', 45.00, 4);
INSERT INTO COURS (typeC, duree, nbParticipantsMax, jour, heureD, prix, idM) VALUES ('Collectif', 1, 6, 'Jeudi', '13:00:00', 20.00, 4);
INSERT INTO COURS (typeC, duree, nbParticipantsMax, jour, heureD, prix, idM) VALUES ('Particulier', 2, 1, 'Vendredi', '15:30:00', 50.00, 4);
-- Echec trigger coursParticulier : un cours particulier ne peut pas avoir plus d'un participant
INSERT INTO COURS (typeC, duree, nbParticipantsMax, jour, heureD, prix, idM) VALUES ('Particulier', 1, 10, 'Samedi', '09:00:00', 20.00, 4);
-- Echec trigger checkDispoMoniteur : le moniteur n'est pas disponible
INSERT INTO COURS (typeC, duree, nbParticipantsMax, jour, heureD, prix, idM) VALUES ('Collectif', 1, 10, 'Mercredi', '15:00:00', 20.00, 4);


INSERT INTO PONEY (nomP, age, poidsSupportableMax) VALUES ('Spirit', 5, 75.0);
INSERT INTO PONEY (nomP, age, poidsSupportableMax) VALUES ('Bella', 8, 60.0);
INSERT INTO PONEY (nomP, age, poidsSupportableMax) VALUES ('Shadow', 7, 70.0);
INSERT INTO PONEY (nomP, age, poidsSupportableMax) VALUES ('Daisy', 6, 65.0);
INSERT INTO PONEY (nomP, age, poidsSupportableMax) VALUES ('Storm', 9, 80.0);


INSERT INTO RESERVATION (idM, poneyID, coursID, coursPayee) VALUES (1, 1, 1, TRUE);
-- Echec trigger poidsInfPoidsMax : le poids de l'adhérent dépasse le poids supportable du poney
INSERT INTO RESERVATION (idM, poneyID, coursID, coursPayee) VALUES (4, 2, 1, TRUE);
-- Echec trigger cotisationPayee : l'adhérent n'a pas payé sa cotisation
INSERT INTO RESERVATION (idM, poneyID, coursID, coursPayee) VALUES (3, 3, 2, TRUE);
INSERT INTO RESERVATION (idM, poneyID, coursID, coursPayee) VALUES (1, 4, 2, TRUE);
-- Echec trigger nbParticipantsMaxAtteint : le nombre maximum de participants est atteint
INSERT INTO RESERVATION (idM, poneyID, coursID, coursPayee) VALUES (2, 5, 2, TRUE);
INSERT INTO RESERVATION (idM, poneyID, coursID, coursPayee) VALUES (1, 1, 4, TRUE);
-- Echec trigger checkReposPoney : le ponney n'a pas eu assez de repos (cours précédent = 1h, cours suivant = 2h donc repos insuffisant)
INSERT INTO RESERVATION (idM, poneyID, coursID, coursPayee) VALUES (1, 1, 5, TRUE);
INSERT INTO RESERVATION (idM, poneyID, coursID, coursPayee) VALUES (1, 1, 6, TRUE);
INSERT INTO RESERVATION (idM, poneyID, coursID, coursPayee) VALUES (2, 1, 7, TRUE); 
INSERT INTO RESERVATION (idM, poneyID, coursID, coursPayee) VALUES (2, 2, 8, TRUE); 
INSERT INTO RESERVATION (idM, poneyID, coursID, coursPayee) VALUES (1, 3, 9, TRUE); 
INSERT INTO RESERVATION (idM, poneyID, coursID, coursPayee) VALUES (2, 3, 9, TRUE); 
INSERT INTO RESERVATION (idM, poneyID, coursID, coursPayee) VALUES (1, 4, 10, TRUE);
-- Echec trigger nbParticipantsMaxAtteint : le nombre maximum de participants est atteint
INSERT INTO RESERVATION (idM, poneyID, coursID, coursPayee) VALUES (2, 5, 10, TRUE);
-- Echec trigger poidsInfPoidsMax : le poids de l'adhérent dépasse le poids supportable du poney
INSERT INTO RESERVATION (idM, poneyID, coursID, coursPayee) VALUES (3, 2, 10, TRUE);


