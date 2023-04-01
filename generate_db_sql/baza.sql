-- Created by Vertabelo (http://vertabelo.com)
-- Last modification date: 2023-04-01 11:14:51.229

-- tables
-- Table: Actor
CREATE TABLE Actor (
    ID_ACTOR SERIAL  PRIMARY KEY,
    name varchar(30)  NOT NULL,
    surname varchar(30)  NOT NULL,
    year_of_birth int  NULL,
    year_of_death int  NULL,
    photo varchar(200)  NULL
);

-- Table: Catalog
CREATE TABLE Catalog (
    ID_CATALOG SERIAL  PRIMARY KEY,
    User_ID_USER int  NOT NULL,
    title varchar(100)  NOT NULL
);

-- Table: Category
CREATE TABLE Category (
    ID_CATEGORY SERIAL  PRIMARY KEY,
    name varchar(50)  NOT NULL
);

CREATE INDEX Category_idx_name on Category USING btree (name ASC);

-- Table: Country
CREATE TABLE Country (
    ID_COUNTRY SERIAL  PRIMARY KEY,
    name varchar(20)  NOT NULL
);

-- Table: Film
CREATE TABLE Film (
    ID_FILM SERIAL  PRIMARY KEY,
    title varchar(80)  NOT NULL,
    poster varchar(200)  NOT NULL,
    director varchar(50)  NOT NULL,
    year int  NOT NULL,
    description text  NOT NULL,
    Country_ID_COUNTRY int  NOT NULL
);

CREATE INDEX Film_idx_title on Film USING btree (title ASC);

-- Table: Film_Actor
CREATE TABLE Film_Actor (
    ID_FILM_ACTOR int  NOT NULL,
    Film_ID_FILM int  NOT NULL,
    Actor_ID_ACTOR int  NOT NULL
);

-- Table: Film_Catalog
CREATE TABLE Film_Catalog (
    ID_FILM_CATALOG SERIAL  PRIMARY KEY,
    Film_ID_FILM int  NOT NULL,
    Catalog_ID_CATALOG int  NOT NULL
);

-- Table: Film_Category
CREATE TABLE Film_Category (
    ID_FILM_CATEGORY SERIAL  PRIMARY KEY,
    Film_ID_FILM int  NOT NULL,
    Category_ID_CATEGORY int  NOT NULL
);

-- Table: Rank
CREATE TABLE Rank (
    ID_RANK SERIAL  PRIMARY KEY,
    name varchar(30)  NOT NULL
);

-- Table: Review
CREATE TABLE Review (
    ID_REVIEW SERIAL  PRIMARY KEY,
    description text  NULL,
    stars int  NOT NULL,
    User_ID_USER int  NOT NULL,
    Film_ID_FILM int  NOT NULL
);

-- Table: User
CREATE TABLE "User" (
    ID_USER SERIAL  PRIMARY KEY,
    mail varchar(30)  NOT NULL,
    password varchar(50)  NOT NULL,
    username varchar(30)  NOT NULL,
    name varchar(30)  NULL,
    surname varchar(30)  NULL,
    Rank_ID_RANK int  NOT NULL
);

-- Table: Watched
CREATE TABLE Watched (
    ID_WATCHED SERIAL  PRIMARY KEY,
    User_ID_USER int  NOT NULL,
    Film_ID_FILM int  NOT NULL
);

-- foreign keys
-- Reference: Catalog_User (table: Catalog)
ALTER TABLE Catalog ADD CONSTRAINT Catalog_User
    FOREIGN KEY (User_ID_USER)
    REFERENCES "User" (ID_USER)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Film_Actor_Actor (table: Film_Actor)
ALTER TABLE Film_Actor ADD CONSTRAINT Film_Actor_Actor
    FOREIGN KEY (Actor_ID_ACTOR)
    REFERENCES Actor (ID_ACTOR)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Film_Actor_Film (table: Film_Actor)
ALTER TABLE Film_Actor ADD CONSTRAINT Film_Actor_Film
    FOREIGN KEY (Film_ID_FILM)
    REFERENCES Film (ID_FILM)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Film_Catalog_Catalog (table: Film_Catalog)
ALTER TABLE Film_Catalog ADD CONSTRAINT Film_Catalog_Catalog
    FOREIGN KEY (Catalog_ID_CATALOG)
    REFERENCES Catalog (ID_CATALOG)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Film_Catalog_Film (table: Film_Catalog)
ALTER TABLE Film_Catalog ADD CONSTRAINT Film_Catalog_Film
    FOREIGN KEY (Film_ID_FILM)
    REFERENCES Film (ID_FILM)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Film_Category_Category (table: Film_Category)
ALTER TABLE Film_Category ADD CONSTRAINT Film_Category_Category
    FOREIGN KEY (Category_ID_CATEGORY)
    REFERENCES Category (ID_CATEGORY)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Film_Category_Film (table: Film_Category)
ALTER TABLE Film_Category ADD CONSTRAINT Film_Category_Film
    FOREIGN KEY (Film_ID_FILM)
    REFERENCES Film (ID_FILM)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Film_Country (table: Film)
ALTER TABLE Film ADD CONSTRAINT Film_Country
    FOREIGN KEY (Country_ID_COUNTRY)
    REFERENCES Country (ID_COUNTRY)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Review_Film (table: Review)
ALTER TABLE Review ADD CONSTRAINT Review_Film
    FOREIGN KEY (Film_ID_FILM)
    REFERENCES Film (ID_FILM)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Review_User (table: Review)
ALTER TABLE Review ADD CONSTRAINT Review_User
    FOREIGN KEY (User_ID_USER)
    REFERENCES "User" (ID_USER)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: User_Rank (table: User)
ALTER TABLE "User" ADD CONSTRAINT User_Rank
    FOREIGN KEY (Rank_ID_RANK)
    REFERENCES Rank (ID_RANK)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Watched_Film (table: Watched)
ALTER TABLE Watched ADD CONSTRAINT Watched_Film
    FOREIGN KEY (Film_ID_FILM)
    REFERENCES Film (ID_FILM)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Watched_User (table: Watched)
ALTER TABLE Watched ADD CONSTRAINT Watched_User
    FOREIGN KEY (User_ID_USER)
    REFERENCES "User" (ID_USER)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- End of file.


