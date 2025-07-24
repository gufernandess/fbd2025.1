ALTER TABLE sono
ADD CONSTRAINT fk_sono_usuario
FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE;

ALTER TABLE humor
ADD CONSTRAINT fk_humor_usuario
FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE;

ALTER TABLE exercicio
ADD CONSTRAINT fk_exercicio_usuario
FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE;

ALTER TABLE hidratacao
ADD CONSTRAINT fk_hidratacao_usuario
FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE;

ALTER TABLE refeicao
ADD CONSTRAINT fk_refeicao_usuario
FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE;

ALTER TABLE meta
ADD CONSTRAINT fk_meta_usuario
FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE;
