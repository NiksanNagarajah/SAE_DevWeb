CREATE TABLE COURS (
  coursID INT(4) PRIMARY KEY AUTO_INCREMENT,
  typeC VARCHAR(42) CHECK (typeC IN ('Collectif', 'particulier')),
  duree INT(4) CHECK (duree IN (1, 2)),
  nbParticipantsMax INT(4) CHECK (nbParticipantsMax <= 10),
  jour VARCHAR(42) CHECK (jour IN ('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche')),
  heureD TIME,
  heureF TIME,
  prix DECIMAL(10,2),
  idM INT(4) NOT NULL
);

CREATE TABLE MEMBRE (
  idM INT(4) PRIMARY KEY AUTO_INCREMENT,
  nomM VARCHAR(42),
  prenomM VARCHAR(42),
  dateNaissance DATE,
  email VARCHAR(42) UNIQUE,
  telephone VARCHAR(42),
  poidsA DECIMAL(10,2),
  niveau VARCHAR(42) NULL,
  idT INT(4) NULL,
  cotisationAnnee INT(4),
  payeeCotisation BOOLEAN,
  certificat VARCHAR(42)
);

CREATE TABLE PONEY (
  poneyID INT(4) PRIMARY KEY AUTO_INCREMENT,
  nomP VARCHAR(42),
  age INT(4),
  poidsSupportableMax DECIMAL(10,2),
  dernierCours DATE, -- DATETIME ???
  disponible BOOLEAN
);

CREATE TABLE RESERVATION (
  PRIMARY KEY (idM, poneyID, coursID),
  idM INT(4) NOT NULL,
  poneyID INT(4) NOT NULL,
  coursID INT(4) NOT NULL,
  coursPayee BOOLEAN
);

-- UTILE ???
-- CREATE TABLE SEANCE (
--   dateSeance DATE,
--   seancePayee BOOLEAN,
--   coursID INT(4) NOT NULL
-- );

CREATE TABLE TARIF (
  PRIMARY KEY (idT),
  idT INT(4) PRIMARY KEY AUTO_INCREMENT,
  descriptif VARCHAR(42),
  montant DECIMAL(10,2)
);

ALTER TABLE COURS ADD FOREIGN KEY (idM) REFERENCES MEMBRE (idM);

ALTER TABLE MEMBRE ADD FOREIGN KEY (idT) REFERENCES TARIF (idT);

ALTER TABLE RESERVATION ADD FOREIGN KEY (coursID) REFERENCES COURS (coursID);
ALTER TABLE RESERVATION ADD FOREIGN KEY (poneyID) REFERENCES PONEY (poneyID);
ALTER TABLE RESERVATION ADD FOREIGN KEY (idM) REFERENCES MEMBRE (idM);

-- ALTER TABLE SEANCE ADD FOREIGN KEY (coursID) REFERENCES COURS (coursID);


-- TRIGGER

-- Vérification du poids du cavalier par rapport au poids supportable maximum du poney
-- Et vérification du nombre de participants
-- Et vérification si l'adhérent a payé sa cotisation avant de pouvoir effectuer une réservation --> Utile ???
DELIMITER |
CREATE OR REPLACE TRIGGER poidsInfPoidsMax 
BEFORE INSERT ON RESERVATION
FOR EACH ROW
BEGIN
  DECLARE poidsCavalier DECIMAL(10,2);
  DECLARE poidsSupportableMax DECIMAL(10,2);
  DECLARE nbParticipantsMax INT(4);
  DECLARE nbParticipantsActuel INT(4);
  -- Utile ???
  DECLARE cotisationPayee BOOLEAN;

  SELECT payeeCotisation INTO cotisationPayee FROM MEMBRE WHERE idM = NEW.idM;
  IF cotisationPayee = FALSE THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'L\'adhérent doit payer sa cotisation avant de pouvoir effectuer une réservation';
  END IF;
  --- end Utile ???

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


