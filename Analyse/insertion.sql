-- INSERT INTO TARIF (descriptif, montant) VALUES 
-- ('Tarif standard', 150.00),
-- ('Tarif réduit', 100.00),
-- ('Tarif famille', 200.00),
-- ('Tarif étudiant', 120.00);

-- INSERT INTO MEMBRE (nomM, prenomM, dateNaissance, email, telephone, poidsA, niveau, idT, cotisationAnnee, payeeCotisation, certificat) VALUES 
-- ('Dupont', 'Alice', '2000-05-15', 'alice.dupont@example.com', '0123456789', 65.00, 'Débutant', 1, 2024, TRUE, 'Certificat A'),
-- ('Martin', 'Bob', '1995-03-22', 'bob.martin@example.com', '0987654321', 80.00, 'Intermédiaire', 2, 2024, TRUE, 'Certificat B'),
-- ('Bernard', 'Charlie', '1985-07-30', 'charlie.bernard@example.com', '0112233445', 95.00, 'Avancé', 3, 2024, FALSE, 'Certificat C'),
-- ('Durand', 'Diane', '1998-12-10', 'diane.durand@example.com', '0123456780', 55.00, 'Débutant', 1, 2024, TRUE, 'Certificat D');

-- INSERT INTO PONEY (nomP, age, poidsSupportableMax, dernierCours, disponible) VALUES 
-- ('Poney1', 5, 70.00, '2024-10-01 10:00:00', TRUE),
-- ('Poney2', 6, 75.00, '2024-10-02 10:00:00', TRUE),
-- ('Poney3', 7, 85.00, '2024-10-03 10:00:00', TRUE),
-- ('Poney4', 8, 90.00, '2024-10-04 10:00:00', FALSE); -- Poney indisponible

-- INSERT INTO COURS (typeC, duree, nbParticipantsMax, jour, heureD, heureF, prix, idM) VALUES 
-- ('Collectif', 2, 10, 'Lundi', '10:00:00', '12:00:00', 30.00, 1),  -- Alice
-- ('particulier', 1, 1, 'Mardi', '14:00:00', '15:00:00', 50.00, 2), -- Bob
-- ('Collectif', 1, 5, 'Mercredi', '09:00:00', '10:00:00', 25.00, 3), -- Charlie
-- ('particulier', 2, 1, 'Jeudi', '16:00:00', '18:00:00', 60.00, 4);  -- Diane

-- INSERT INTO RESERVATION (idM, poneyID, coursID, coursPayee) VALUES 
-- (1, 1, 1, TRUE),  -- Alice avec Poney1 pour un cours collectif
-- (2, 2, 2, TRUE),  -- Bob avec Poney2 pour un cours particulier
-- (3, 3, 3, TRUE);  -- Charlie avec Poney3 pour un cours collectif
-- INSERT INTO RESERVATION (idM, poneyID, coursID, coursPayee) VALUES (4, 4, 4, TRUE);  -- Diane avec Poney4 pour un cours particulier (devrait échouer car Poney4 est indisponible)

INSERT INTO TARIF (descriptif, montant) VALUES
('Adhésion Année Complète', 120.00),
('Cours Particulier', 50.00),
('Cours Collectif', 30.00),
('Assurance', 20.00);

INSERT INTO MEMBRE (nomM, prenomM, dateNaissance, email, telephone, poidsA, niveau, idT, cotisationAnnee, payeeCotisation, certificat) VALUES
('Dupont', 'Marie', '1990-05-12', 'marie.dupont@example.com', '0123456789', 55.00, 'Débutant', 1, 2024, TRUE, NULL),  -- Adhérent
('Martin', 'Pierre', '1985-04-15', 'pierre.martin@example.com', '0987654321', 75.00, 'Intermédiaire', 1, 2024, TRUE, NULL),  -- Adhérent
('Lebrun', 'Sophie', '1992-06-20', 'sophie.lebrun@example.com', '0147852369', 68.00, 'Avancé', 1, 2024, FALSE, NULL),  -- Adhérent (cotisation non payée)
('Lemoine', 'Luc', '1980-11-30', 'luc.lemoine@example.com', '0654321789', 82.00, 'Moniteur', 1, 2024, TRUE, 'Certificat A'),  -- Moniteur
('Rousseau', 'Alice', '1995-08-15', 'alice.rousseau@example.com', '0671234567', 60.00, 'Moniteur', 1, 2024, TRUE, 'Certificat B');  -- Moniteur

INSERT INTO PONEY (nomP, age, poidsSupportableMax, dernierCours, disponible) VALUES
('Poney1', 5, 100.00, '2024-10-15 10:00:00', TRUE),
('Poney2', 6, 120.00, '2024-10-14 11:00:00', TRUE),
('Poney3', 7, 90.00, '2024-10-13 09:00:00', FALSE),
('Poney4', 4, 80.00, '2024-10-20 14:00:00', TRUE),
('Poney5', 8, 110.00, '2024-10-16 12:00:00', TRUE);

INSERT INTO COURS (typeC, duree, nbParticipantsMax, jour, heureD, heureF, prix, idM) VALUES
('Collectif', 1, 10, 'Lundi', '09:00:00', '10:00:00', 30.00, 4),  -- Cours collectif avec le moniteur Luc
('Particulier', 1, 1, 'Mardi', '10:00:00', '11:00:00', 50.00, 5),  -- Cours particulier avec le moniteur Alice
('Collectif', 2, 10, 'Mercredi', '15:00:00', '17:00:00', 60.00, 4),  -- Cours collectif
('Particulier', 1, 1, 'Jeudi', '16:00:00', '17:00:00', 50.00, 4),  -- Cours particulier
('Collectif', 1, 8, 'Vendredi', '18:00:00', '19:00:00', 30.00, 4);  -- Cours collectif

INSERT INTO RESERVATION (idM, poneyID, coursID, coursPayee) VALUES
(1, 1, 1, TRUE),  -- Marie avec Poney1 pour un cours collectif
(2, 2, 2, TRUE),  -- Pierre avec Poney2 pour un cours particulier
(1, 4, 4, TRUE),  -- Marie avec Poney4 pour un cours particulier
(2, 5, 5, TRUE);  -- Pierre avec Poney5 pour un cours collectif

-- Réservations pour tester les triggers
INSERT INTO RESERVATION (idM, poneyID, coursID, coursPayee) VALUES (3, 3, 3, FALSE),  -- Sophie avec Poney3 pour un cours collectif (cotisation non payée)


