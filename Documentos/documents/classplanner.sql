/* Lógico-ClassPlanner */

CREATE TABLE Professor (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Nome VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    User VARCHAR(100) NOT NULL
);

CREATE TABLE Disciplina (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Nome VARCHAR(100) NOT NULL,
    Cor VARCHAR(7),
    fk_professor_id INT NOT NULL,
    CONSTRAINT FK_Disciplina_Professor FOREIGN KEY (fk_professor_id)
        REFERENCES Professor(ID)
        ON DELETE CASCADE
);

CREATE TABLE Tema (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Nome VARCHAR(100) NOT NULL,
    fk_disciplina_id INT NOT NULL,
    CONSTRAINT FK_Tema_Disciplina FOREIGN KEY (fk_disciplina_id)
        REFERENCES Disciplina(ID)
        ON DELETE CASCADE
);

CREATE TABLE Conteudos (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Descricao VARCHAR(255) NOT NULL,
    fk_tema_id INT NOT NULL,
    CONSTRAINT FK_Conteudos_Tema FOREIGN KEY (fk_tema_id)
        REFERENCES Tema(ID)
        ON DELETE CASCADE
);

CREATE TABLE Aluno (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Nome VARCHAR(100) NOT NULL,
    Telefone VARCHAR(20)
);

CREATE TABLE Matricula (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Status VARCHAR(50),
    Ultimo_pagamento DATE,
    Data DATE,
    Anotacoes TEXT,
    fk_disciplina_id INT NOT NULL,
    fk_aluno_id INT NOT NULL,
    CONSTRAINT FK_Matricula_Disciplina FOREIGN KEY (fk_disciplina_id)
        REFERENCES Disciplina(ID)
        ON DELETE CASCADE,
    CONSTRAINT FK_Matricula_Aluno FOREIGN KEY (fk_aluno_id)
        REFERENCES Aluno(ID)
        ON DELETE CASCADE
);

CREATE TABLE Aula (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Data_Hora_Inicio DATETIME NOT NULL,
    Data_Hora_Fim DATETIME NOT NULL,
    Recorrente BOOLEAN DEFAULT FALSE,
    fk_matricula_id INT NOT NULL,
    CONSTRAINT FK_Aula_Matricula FOREIGN KEY (fk_matricula_id)
        REFERENCES Matricula(ID)
        ON DELETE CASCADE
);

CREATE TABLE Contem (
    fk_aula_id INT,
    fk_conteudos_id INT,
    PRIMARY KEY (fk_aula_id, fk_conteudos_id),
    CONSTRAINT FK_Contem_Aula FOREIGN KEY (fk_aula_id)
        REFERENCES Aula(ID)
        ON DELETE CASCADE,
    CONSTRAINT FK_Contem_Conteudos FOREIGN KEY (fk_conteudos_id)
        REFERENCES Conteudos(ID)
        ON DELETE CASCADE
);

ALTER TABLE Disciplina 
ADD CONSTRAINT FK_Disciplina_Professor
    FOREIGN KEY (fk_Professor_ID)
    REFERENCES Professor(ID)
    ON DELETE CASCADE;

ALTER TABLE Tema 
ADD CONSTRAINT FK_Tema_Disciplina
    FOREIGN KEY (fk_Disciplina_ID)
    REFERENCES Disciplina(ID)
    ON DELETE CASCADE;

ALTER TABLE Conteudos 
ADD CONSTRAINT FK_Conteudos_Tema
    FOREIGN KEY (fk_Tema_ID)
    REFERENCES Tema(ID)
    ON DELETE CASCADE;

ALTER TABLE Matricula 
ADD CONSTRAINT FK_Matricula_Disciplina
    FOREIGN KEY (fk_Disciplina_ID)
    REFERENCES Disciplina(ID)
    ON DELETE CASCADE;

ALTER TABLE Matricula 
ADD CONSTRAINT FK_Matricula_Aluno
    FOREIGN KEY (fk_Aluno_ID)
    REFERENCES Aluno(ID)
    ON DELETE CASCADE;

ALTER TABLE Aula 
ADD CONSTRAINT FK_Aula_Matricula
    FOREIGN KEY (fk_Matricula_ID)
    REFERENCES Matricula(ID)
    ON DELETE CASCADE;

ALTER TABLE Contem 
ADD CONSTRAINT FK_Contem_Aulas
    FOREIGN KEY (fk_Aula_ID)
    REFERENCES Aula(ID)
    ON DELETE CASCADE;

ALTER TABLE Contem 
ADD CONSTRAINT FK_Contem_Conteudos
    FOREIGN KEY (fk_Conteudos_ID)
    REFERENCES Conteudos(ID)
    ON DELETE CASCADE;