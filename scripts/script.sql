CREATE TABLE usuario (
    id_usuario SERIAL PRIMARY KEY,
    nome_usuario VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    data_criacao_conta TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE sono (
    id_sono SERIAL PRIMARY KEY,
    data_inicio_sono TIMESTAMP WITH TIME ZONE NOT NULL,
    data_fim_sono TIMESTAMP WITH TIME ZONE NOT NULL,
    duracao_minutos INT,
    qualidade_sono INT,
    id_usuario INT NOT NULL
);

CREATE TABLE humor (
    id_humor SERIAL PRIMARY KEY,
    estado_humor VARCHAR(50) NOT NULL,
    nota_contexto TEXT,
    data_registro TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    id_usuario INT NOT NULL
);

CREATE TABLE exercicio (
    id_exercicio SERIAL PRIMARY KEY,
    tipo_exercicio VARCHAR(100) NOT NULL,
    duracao_minutos INT NOT NULL,
    notas_exercicio TEXT,
    data_exercicio TIMESTAMP WITH TIME ZONE NOT NULL,
    id_usuario INT NOT NULL
);

CREATE TABLE hidratacao (
    id_hidratacao SERIAL PRIMARY KEY,
    quantidade_ml INT NOT NULL,
    data_hidratacao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    id_usuario INT NOT NULL
);

CREATE TABLE refeicao (
    id_refeicao SERIAL PRIMARY KEY,
    tipo_refeicao VARCHAR(50) NOT NULL,
    descricao_refeicao TEXT NOT NULL,
    foto_refeicao VARCHAR(255),
    data_refeicao TIMESTAMP WITH TIME ZONE NOT NULL,
    id_usuario INT NOT NULL
);

CREATE TABLE meta (
    id_meta SERIAL PRIMARY KEY,
    tipo_meta VARCHAR(100) NOT NULL,
    valor_meta DECIMAL(10, 2) NOT NULL,
    unidade_meta VARCHAR(50) NOT NULL,
    data_meta DATE,
    id_usuario INT NOT NULL,
    UNIQUE (id_usuario, tipo_meta, data_meta)
);
