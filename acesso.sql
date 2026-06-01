CREATE TABLE ADV_Usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nm_usuario VARCHAR(255) NOT NULL UNIQUE,
    bo_ativo BOOLEAN DEFAULT TRUE
);

CREATE TABLE ADV_Sehnas (
    id_senha SERIAL PRIMARY KEY,
    id_usuario INT NOT NULL REFERENCES ADV_Usuarios(id_usuario),
    nm_senha VARCHAR(255) NOT NULL, -- Salva a senha como MD5 hash
    bo_ativo BOOLEAN DEFAULT TRUE
);

SELECT * FROM ADV_Usuarios
INSERT INTO  ADV_Usuarios (nm_usuario, bo_ativo)
VALUES ('Sergio Renato', 't'), ('Jose Amaral', 't'), ('Julio Cesar', 't'), ('Everton Flech', 't')

SELECT * FROM adv_sehnas
INSERT INTO adv_sehnas (id_usuario, nm_senha, bo_ativo)
VALUES (1, MD5('123'), 't'), (2, MD5('123'), 't'), (3, MD5('123'),'f'), (4, MD5('123'),'f')