CREATE TABLE COURS (
  PRIMARY KEY (coursID),
  coursID INT(4) NOT NULL,
  typeC VARCHAR(42) CHECK (typeC IN ('Collectif', 'particulier')),
  duree TIME,
  nbParticipants INT(4),
  jour VARCHAR(42),
  heureD TIME,
  heureF TIME,
  prix DECIMAL(10,2),
  idM INT(4) NOT NULL
);

CREATE TABLE MEMBRE (
  PRIMARY KEY (idM),
  idM INT(4) NOT NULL,
  nomM VARCHAR(42),
  prenomM VARCHAR(42),
  dateNaissance DATE,
  email VARCHAR(42),
  telephone VARCHAR(42),
  poidsA DECIMAL(10,2) NULL,
  niveau VARCHAR(42) NULL,
  idT INT(4) NULL,
  cotisationAnnee INT(4) NULL,
  payeeCotisation BOOLEAN NULL,
  certificat VARCHAR(42) NULL
);

CREATE TABLE PONEY (
  PRIMARY KEY (poneyID),
  poneyID INT(4) NOT NULL,
  nomP VARCHAR(42),
  age INT(4),
  poidsMaxCavalier DECIMAL(10,2),
  dernierCours DATE,
  tempsRepos INT(4)
);

CREATE TABLE RESERVATION (
  PRIMARY KEY (idM, poneyID, coursID),
  idM INT(4) NOT NULL,
  poneyID INT(4) NOT NULL,
  coursID INT(4) NOT NULL,
  coursPayee BOOLEAN
);

CREATE TABLE SEANCE (
  dateSeance DATE,
  seancePayee BOOLEAN,
  coursID INT(4) NOT NULL
);

CREATE TABLE TARIF (
  PRIMARY KEY (idT),
  idT INT(4) NOT NULL,
  descriptif VARCHAR(42),
  montant DECIMAL(10,2)
);

ALTER TABLE COURS ADD FOREIGN KEY (idM) REFERENCES MEMBRE (idM);

ALTER TABLE MEMBRE ADD FOREIGN KEY (idT) REFERENCES TARIF (idT);

ALTER TABLE RESERVATION ADD FOREIGN KEY (coursID) REFERENCES COURS (coursID);
ALTER TABLE RESERVATION ADD FOREIGN KEY (poneyID) REFERENCES PONEY (poneyID);
ALTER TABLE RESERVATION ADD FOREIGN KEY (idM) REFERENCES MEMBRE (idM);

ALTER TABLE SEANCE ADD FOREIGN KEY (coursID) REFERENCES COURS (coursID);


-- Trigger à revoir
DELIMITER |
CREATE OR REPLACE TRIGGER poidsInfPoidsMax BEFORE INSERT ON MEMBRE
FOR EACH ROW
BEGIN
  IF (SELECT poidsMaxCavalier FROM PONEY WHERE poneyID = :NEW.idM) < :NEW.poidsA THEN
    RAISE_APPLICATION_ERROR(-20001, 'Le poids du cavalier est supérieur au poids maximum du poney');
  END IF;
END |
DELIMITER ;