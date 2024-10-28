DROP TABLE IF EXISTS RESERVATION;
DROP TABLE IF EXISTS COURS;
DROP TABLE IF EXISTS MEMBRE;
DROP TABLE IF EXISTS TARIF;
DROP TABLE IF EXISTS PONEY;

CREATE TABLE TARIF (
    idT INT(4) PRIMARY KEY AUTO_INCREMENT,
    descriptif VARCHAR(42),
    montant DECIMAL(10,2)
);

CREATE TABLE MEMBRE (
    idM INT(4) PRIMARY KEY AUTO_INCREMENT,
    nomM VARCHAR(42),
    prenomM VARCHAR(42),
    dateNaissance DATE,
    email VARCHAR(42) UNIQUE,
    motDePasse VARCHAR(100),
    telephone VARCHAR(42),
    poidsA DECIMAL(10,2) NULL,
    niveau VARCHAR(42) NULL,
    idT INT(4) NULL,
    cotisationAnnee INT(4) NULL,
    cotisationPayee BOOLEAN DEFAULT FALSE NULL,
    anneeExperience VARCHAR(42) NULL,
    roleM ENUM('Adhérent', 'Moniteur', 'Administrateur'),
    FOREIGN KEY (idT) REFERENCES TARIF (idT) -- Ajout de la clé étrangère ici
);

CREATE TABLE COURS (
    coursID INT(4) PRIMARY KEY AUTO_INCREMENT,
    typeC ENUM('Collectif', 'Particulier'), -- Utilisation d'ENUM pour les types
    duree INT(1) CHECK (duree IN (1, 2)), -- Limite à 1 ou 2 heures
    nbParticipantsMax INT(4) DEFAULT 10 CHECK (nbParticipantsMax <= 10), -- Ajout d'une valeur par défaut
    jour ENUM('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'), -- Utilisation d'ENUM
    heureD TIME,
    heureF TIME DEFAULT ADDTIME(heureD, duree * 10000), -- Calcul de l'heure de fin
    prix DECIMAL(10,2),
    idM INT(4) NOT NULL,
    FOREIGN KEY (idM) REFERENCES MEMBRE (idM) -- Ajout de la clé étrangère directement ici
);

CREATE TABLE PONEY (
    poneyID INT(4) PRIMARY KEY AUTO_INCREMENT,
    nomP VARCHAR(42),
    age INT(4),
    poidsSupportableMax DECIMAL(10,2)
    -- dernierCours DATETIME,
    -- disponible BOOLEAN
);

CREATE TABLE RESERVATION (
    idM INT(4) NOT NULL,
    poneyID INT(4) NOT NULL,
    coursID INT(4) NOT NULL,
    coursPayee BOOLEAN,
    PRIMARY KEY (idM, poneyID, coursID),
    FOREIGN KEY (coursID) REFERENCES COURS (coursID),
    FOREIGN KEY (poneyID) REFERENCES PONEY (poneyID),
    FOREIGN KEY (idM) REFERENCES MEMBRE (idM)
);

-- TRIGGER

-- Vérification du poids du cavalier par rapport au poids supportable maximum du poney
-- Et vérification du nombre de participants
-- Et vérification si l'adhérent a payé sa cotisation avant de pouvoir effectuer une réservation
DELIMITER |
CREATE OR REPLACE TRIGGER poidsInfPoidsMax 
BEFORE INSERT ON RESERVATION
FOR EACH ROW
BEGIN
  DECLARE poidsCavalier DECIMAL(10,2);
  DECLARE poidsSupportableMax DECIMAL(10,2);
  DECLARE nbParticipantsMax INT(4);
  DECLARE nbParticipantsActuel INT(4);
  DECLARE cotisationPayee BOOLEAN;

  SELECT cotisationPayee INTO cotisationPayee FROM MEMBRE WHERE idM = NEW.idM;
  IF cotisationPayee = FALSE THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'L\'adhérent doit payer sa cotisation avant de pouvoir effectuer une réservation';
  END IF;

  SELECT nbParticipantsMax INTO nbParticipantsMax FROM COURS WHERE coursID = NEW.coursID;
  SELECT COUNT(*) INTO nbParticipantsActuel FROM RESERVATION WHERE coursID = NEW.coursID;

  IF nbParticipantsActuel + 1 > nbParticipantsMax THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Le nombre de participants maximum est atteint';
  END IF;

  SELECT poidsA INTO poidsCavalier FROM MEMBRE WHERE idM = NEW.idM;
  SELECT poidsSupportableMax INTO poidsSupportableMax FROM PONEY WHERE poneyID = NEW.poneyID;

  IF poidsSupportableMax < poidsCavalier THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Le poids du cavalier est supérieur au poids supportable maximum du poney';
  END IF;
END |
DELIMITER ;

-- Vérification de si c'est un cours particulier, alors il ne peut y avoir qu'un seul participant
DELIMITER |
CREATE OR REPLACE TRIGGER coursParticulier
BEFORE INSERT ON COURS
FOR EACH ROW
BEGIN 
  IF NEW.typeC = 'Particulier' AND NEW.nbParticipantsMax > 1 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Un cours particulier ne peut avoir qu\'un seul participant';
  END IF;
END |
DELIMITER ;

DELIMITER |
CREATE OR REPLACE TRIGGER checkReposPoney
BEFORE INSERT ON RESERVATION
FOR EACH ROW
BEGIN
    DECLARE coursDuree INT(1);
    DECLARE finCours TIME;
    DECLARE derniereReservation TIME;
    DECLARE jourCours ENUM('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche');
    DECLARE heureCours TIME;
    DECLARE tempsRepos INT;
    DECLARE totalDuree INT DEFAULT 0;

    -- Récupérer la durée du cours et les horaires du cours à réserver
    SELECT duree, jour, heureD INTO coursDuree, jourCours, heureCours FROM COURS WHERE coursID = NEW.coursID;

    -- Calculer l'heure de fin du cours
    SET finCours = ADDTIME(heureCours, coursDuree * 10000);

    -- Vérifier les réservations précédentes pour le même poney
    SELECT MAX(heureF) INTO derniereReservation
    FROM RESERVATION R JOIN COURS C ON R.coursID = C.coursID
    WHERE R.poneyID = NEW.poneyID 
      AND C.jour = jourCours 
      AND C.heureD < heureCours; -- Vérifie que les cours précédents se terminent avant le début du nouveau cours

    -- Vérifier si le poney a eu des cours précédents
    IF derniereReservation IS NOT NULL THEN
        -- Calculer le temps de repos
        SET tempsRepos = TIMESTAMPDIFF(MINUTE, derniereReservation, heureCours); -- Temps de repos en minutes

        -- Si le temps de repos est de 60 minutes ou plus, autoriser la réservation
        IF tempsRepos < 60 THEN

          -- Calculer la durée des cours précédents
          SELECT SUM(C.duree) INTO totalDuree
          FROM RESERVATION R JOIN COURS C ON R.coursID = C.coursID
          WHERE R.poneyID = NEW.poneyID 
            AND C.jour = jourCours 
            AND C.heureD < heureCours 
            AND C.heureF <= derniereReservation; -- On s'assure qu'on ne dépasse pas la dernière réservation

          -- Conditions à vérifier
          -- Si la somme des durées des cours précédents dépasse 1 heure et que le nouveau cours est de 2 heures
          IF (totalDuree >= 2 AND coursDuree = 2) THEN
              SIGNAL SQLSTATE '45000' 
              SET MESSAGE_TEXT = 'Le poney doit se reposer après avoir eu au moins 2 heures de cours.';
          END IF;

          -- Si la somme des durées des cours précédents est exactement 2 heures et le nouveau cours est de 1 heure
          IF (totalDuree = 2 AND coursDuree = 1) THEN
              SIGNAL SQLSTATE '45000' 
              SET MESSAGE_TEXT = 'Le poney doit se reposer après avoir eu 2 heures de cours.';
          END IF;

          -- Si la somme des durées des cours précédents est 1 heure et le nouveau cours est de 2 heures
          IF (totalDuree = 1 AND coursDuree = 2) THEN
              SIGNAL SQLSTATE '45000' 
              SET MESSAGE_TEXT = 'Le poney doit se reposer après avoir eu 1 heure de cours avant un cours de 2 heures.';
          END IF;
        END IF;
    END IF;
END |
DELIMITER ;
