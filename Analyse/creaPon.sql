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
    anneeExperience INT(2) NULL,
    roleM ENUM('Adhérent', 'Moniteur', 'Administrateur'),
    FOREIGN KEY (idT) REFERENCES TARIF (idT)
);

CREATE TABLE COURS (
    coursID INT(4) PRIMARY KEY AUTO_INCREMENT,
    typeC ENUM('Collectif', 'Particulier'), -- Utilisation d'ENUM pour les types
    duree INT(1) CHECK (duree IN (1, 2)), -- Limite à 1 ou 2 heures
    nbParticipantsMax INT(4) DEFAULT 10 CHECK (nbParticipantsMax <= 10), 
    jour ENUM('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'),
    heureD TIME,
    heureF TIME DEFAULT ADDTIME(heureD, duree * 10000), -- Calcul de l'heure de fin
    prix DECIMAL(10,2),
    idM INT(4) NOT NULL,
    FOREIGN KEY (idM) REFERENCES MEMBRE (idM) 
);

CREATE TABLE PONEY (
    poneyID INT(4) PRIMARY KEY AUTO_INCREMENT,
    nomP VARCHAR(42),
    age INT(4),
    poidsSupportableMax DECIMAL(10,2)
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

-- Vérifie si le poids du cavalier est inférieur au poids supportable maximum du poney
DELIMITER |
CREATE OR REPLACE TRIGGER poidsInfPoidsMax 
BEFORE INSERT ON RESERVATION
FOR EACH ROW
BEGIN
  DECLARE poidsCavalier DECIMAL(10,2);
  DECLARE poidsSupportableMaxPoney DECIMAL(10,2);

  SELECT poidsA INTO poidsCavalier FROM MEMBRE WHERE idM = NEW.idM;
  SELECT poidsSupportableMax INTO poidsSupportableMaxPoney FROM PONEY WHERE poneyID = NEW.poneyID;

  IF poidsSupportableMaxPoney < poidsCavalier THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Le poids du cavalier est supérieur au poids supportable maximum du poney';
  END IF;
END |
DELIMITER ;

-- Vérifie si le membre est un moniteur, s'il l'est, il ne peut pas effectuer de réservation
DELIMITER |
CREATE OR REPLACE TRIGGER moniteurNePeutPasReserver
BEFORE INSERT ON RESERVATION
FOR EACH ROW
BEGIN
  DECLARE roleMembre ENUM('Adhérent', 'Moniteur', 'Administrateur');

  SELECT roleM INTO roleMembre FROM MEMBRE WHERE idM = NEW.idM;

  IF roleMembre = 'Moniteur' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Un moniteur ne peut pas effectuer de réservation';
  END IF;
END |
DELIMITER ;

-- Vérifie si le nombre de participants maximum est atteint
DELIMITER |
CREATE OR REPLACE TRIGGER nbParticipantsMaxAtteint
BEFORE INSERT ON RESERVATION
FOR EACH ROW
BEGIN
  DECLARE nbParticipantsMaxCours INT(4);
  DECLARE nbParticipantsActuel INT(4);

  SELECT nbParticipantsMax INTO nbParticipantsMaxCours FROM COURS WHERE coursID = NEW.coursID;
  SELECT COUNT(*) INTO nbParticipantsActuel FROM RESERVATION WHERE coursID = NEW.coursID;

  IF nbParticipantsActuel + 1 > nbParticipantsMaxCours THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Le nombre de participants maximum est atteint';
  END IF;
END |
DELIMITER ;

-- Vérifie si l'adhérent a payé sa cotisation avant de pouvoir effectuer une réservation
DELIMITER |
CREATE OR REPLACE TRIGGER cotisationPayee
BEFORE INSERT ON RESERVATION
FOR EACH ROW
BEGIN
  DECLARE cotisationEstPayee BOOLEAN;

  SELECT cotisationPayee INTO cotisationEstPayee FROM MEMBRE WHERE idM = NEW.idM;

  IF cotisationEstPayee = FALSE THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'L\'adhérent doit payer sa cotisation avant de pouvoir effectuer une réservation';
  END IF;
END |
DELIMITER ;

-- Vérifie si c'est un cours particulier, si oui, alors il ne peut y avoir qu'un seul participant
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

-- Vérifie si le poney est disponible avant de pouvoir effectuer une réservation
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

    SELECT duree, jour, heureD INTO coursDuree, jourCours, heureCours FROM COURS WHERE coursID = NEW.coursID;
    SET finCours = ADDTIME(heureCours, coursDuree * 10000);

    -- Vérifier les réservations précédentes pour le même poney
    SELECT MAX(heureF) INTO derniereReservation
    FROM RESERVATION R JOIN COURS C ON R.coursID = C.coursID
    WHERE R.poneyID = NEW.poneyID 
      AND C.jour = jourCours 
      AND C.heureD < heureCours; 

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
            AND C.heureF <= derniereReservation; 

          IF (totalDuree >= 2 AND coursDuree = 2) THEN
              SIGNAL SQLSTATE '45000' 
              SET MESSAGE_TEXT = 'Le poney doit se reposer après avoir eu au moins 2 heures de cours.';
          END IF;

          IF (totalDuree = 2 AND coursDuree = 1) THEN
              SIGNAL SQLSTATE '45000' 
              SET MESSAGE_TEXT = 'Le poney doit se reposer après avoir eu 2 heures de cours.';
          END IF;

          IF (totalDuree = 1 AND coursDuree = 2) THEN
              SIGNAL SQLSTATE '45000' 
              SET MESSAGE_TEXT = 'Le poney doit se reposer après avoir eu 1 heure de cours avant un cours de 2 heures.';
          END IF;
        END IF;
    END IF;
END |
DELIMITER ;

-- Vérifie si le poney est déjà réservé à cet horaire et si le membre est déjà inscrit à un autre cours à cet horaire
DELIMITER |
CREATE OR REPLACE TRIGGER checkChevauchementReservation
BEFORE INSERT ON RESERVATION
FOR EACH ROW
BEGIN
    DECLARE horaireCoursNewDebut TIME;
    DECLARE horaireCoursNewFin TIME;
    DECLARE horaireCoursExistantDebut TIME;
    DECLARE horaireCoursExistantFin TIME;
    DECLARE poneyConflit INT;
    DECLARE membreConflit INT;
    
    -- Récupérer les horaires du nouveau cours à réserver
    SELECT heureD, heureF INTO horaireCoursNewDebut, horaireCoursNewFin 
    FROM COURS WHERE coursID = NEW.coursID;
    
    -- Vérifier s'il y a un conflit d'horaire pour le même poney
    SELECT COUNT(*) INTO poneyConflit
    FROM RESERVATION R 
    JOIN COURS C ON R.coursID = C.coursID
    WHERE R.poneyID = NEW.poneyID
    AND (
        (C.heureD < horaireCoursNewFin AND C.heureF > horaireCoursNewDebut)  -- Chevauchement de temps
    );
    
    -- Vérifier s'il y a un conflit d'horaire pour le même membre
    SELECT COUNT(*) INTO membreConflit
    FROM RESERVATION R 
    JOIN COURS C ON R.coursID = C.coursID
    WHERE R.idM = NEW.idM
    AND (
        (C.heureD < horaireCoursNewFin AND C.heureF > horaireCoursNewDebut)  -- Chevauchement de temps
    );

    -- Si un conflit pour le poney est trouvé, empêcher la réservation
    IF poneyConflit > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Le poney est déjà réservé à cet horaire.';
    END IF;

    -- Si un conflit pour le membre est trouvé, empêcher la réservation
    IF membreConflit > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Le membre est déjà inscrit à un autre cours à cet horaire.';
    END IF;
END |
DELIMITER ;

-- Vérifie si le moniteur est disponible avant de pouvoir effectuer une réservation
DELIMITER |
CREATE OR REPLACE TRIGGER checkDispoMoniteur
BEFORE INSERT ON COURS
FOR EACH ROW
BEGIN
    DECLARE heureFinNouveauCours TIME;
    DECLARE conflit INT;
    DECLARE messageErreur VARCHAR(255);

    -- Récupérer l'heure de fin du nouveau cours
    SET heureFinNouveauCours = ADDTIME(NEW.heureD, NEW.duree * 10000);

    -- Vérifier si le moniteur a un autre cours qui chevauche le nouvel horaire
    SELECT COUNT(*) INTO conflit
    FROM COURS
    WHERE idM = NEW.idM 
      AND jour = NEW.jour 
      AND (
            (NEW.heureD < heureF AND heureD < heureFinNouveauCours) -- Vérifier chevauchement
            AND NOT (NEW.heureD = heureF OR heureD = heureFinNouveauCours) -- Autoriser les cours consécutifs sans chevauchement
          );

    -- Si un conflit est détecté, bloquer l'insertion avec un message d'erreur contenant le nombre de conflits
    IF conflit > 0 THEN
        SET messageErreur = CONCAT('Le moniteur n\'est pas disponible pour cet horaire, il a déjà ', CAST(conflit AS CHAR), ' cours prévu(s).');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = messageErreur;
    END IF;
END |
DELIMITER ;



