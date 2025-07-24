INSERT INTO usuario (nome_usuario, email, senha_hash, data_criacao_conta) VALUES
('Ana Silva', 'ana.silva@example.com', '$2b$12$EIK4g.IIXJcT9r6lqF1jgu3fVd/sXkC5YILJ4A0h2P4z0b8cW3yvC', '2025-01-15 10:00:00'),
('Bruno Costa', 'bruno.costa@example.com', '$2b$12$L9mN.oP1qR2sT3uV4wX5y.Z/aB7c8D9e0F1g2H3i4J5k6L7m.n', '2025-01-20 11:30:00'),
('Carla Martins', 'carla.martins@example.com', '$2b$12$T5oP6qR7sT8uV9wX.yZ.aB.c4D5e6F7g8H9i0J1k2L3m4N5oP', '2025-02-10 14:00:00'),
('Daniel Oliveira', 'daniel.oliveira@example.com', '$2b$12$uV.wX0y1Z2aB3c4D5eF6g.H/iJ8k9L0m1N2o3P4q5R6s7T8u.v', '2025-02-25 09:45:00'),
('Eduarda Pereira', 'eduarda.pereira@example.com', '$2b$12$xZ.yv3.4u6T2Bq7A8c9d0e.fG/hI1jK3L4mN5oP6qR7sT8uV9wX.z', '2025-03-05 18:20:00'),
('Felipe Almeida', 'felipe.almeida@example.com', '$2b$12$aB.cD1e2F3gH4iJ5kL6mN.oP/qR7sT8uV9wX0yZ1a2B3c4D5e6F.g', '2025-03-12 20:00:00'),
('Gabriela Santos', 'gabriela.santos@example.com', '$2b$12$sT.uV9w0X1yZ2aB3c4D5e.F/gH7i8J9k0L1m2N3o4P5q6R7s.t', '2025-04-01 12:10:00'),
('Heitor Lima', 'heitor.lima@example.com', '$2b$12$hI.jK3l4M5nO6pQ7rS8tU.vW/xY9z0A1b2C3d4E5fG6h7I8j.k', '2025-04-15 08:00:00'),
('Isabela Ferreira', 'isabela.ferreira@example.com', '$2b$12$qR.sT8u9V0wX1yZ2aB3c4.D/eF6g7H8i9J0k1L2m3N4o5P6q.r', '2025-05-02 22:00:00'),
('João Souza', 'joao.souza@example.com', '$2b$12$wX.yZ1a2B3c4D5eF6gH7i.J/kL9m0N1o2P3q4R5s6T7u8V9w.x', '2025-05-10 16:50:00');


INSERT INTO sono (id_usuario, data_inicio_sono, data_fim_sono, duracao_minutos, qualidade_sono) VALUES
(1, '2025-07-20 22:00:00', '2025-07-21 06:00:00', 480, 5),
(2, '2025-07-20 23:30:00', '2025-07-21 07:00:00', 450, 4),
(3, '2025-07-20 21:45:00', '2025-07-21 05:30:00', 465, 4),
(4, '2025-07-21 00:15:00', '2025-07-21 08:00:00', 465, 5),
(5, '2025-07-21 22:30:00', '2025-07-22 05:30:00', 420, 3),
(1, '2025-07-21 22:10:00', '2025-07-22 06:15:00', 485, 5),
(6, '2025-07-21 23:00:00', '2025-07-22 07:30:00', 510, 5),
(7, '2025-07-21 21:30:00', '2025-07-22 04:45:00', 435, 3),
(8, '2025-07-21 22:45:00', '2025-07-22 06:45:00', 480, 4),
(10, '2025-07-22 01:00:00', '2025-07-22 09:00:00', 480, 4);

INSERT INTO humor (id_usuario, estado_humor, nota_contexto, data_registro) VALUES
(1, 'Feliz', 'Dia produtivo no trabalho.', '2025-07-21 09:00:00'),
(2, 'Cansado', 'Dormi pouco na noite anterior.', '2025-07-21 10:15:00'),
(3, 'Ansiosa', 'Tenho uma apresentação importante amanhã.', '2025-07-21 14:00:00'),
(5, 'Normal', 'Um dia tranquilo, sem novidades.', '2025-07-21 15:30:00'),
(7, 'Animada', 'Encontrei com amigos para almoçar.', '2025-07-21 18:00:00'),
(9, 'Estressada', 'Muito trânsito na volta para casa.', '2025-07-21 19:20:00'),
(4, 'Relaxado', 'Consegui meditar por 15 minutos.', '2025-07-22 08:30:00'),
(6, 'Feliz', 'Recebi uma boa notícia pessoal.', '2025-07-22 09:45:00'),
(8, 'Motivado', 'Comecei um novo projeto.', '2025-07-22 10:00:00'),
(10, 'Sonolento', 'Ainda me recuperando do final de semana.', '2025-07-22 10:30:00');

INSERT INTO exercicio (id_usuario, tipo_exercicio, duracao_minutos, notas_exercicio, data_exercicio) VALUES
(1, 'Caminhada', 30, 'Caminhada leve no parque.', '2025-07-21 07:00:00'),
(2, 'Musculação', 60, 'Treino de peito e tríceps.', '2025-07-21 18:00:00'),
(4, 'Corrida', 45, 'Corrida de 5km na esteira.', '2025-07-21 19:00:00'),
(7, 'Yoga', 50, 'Aula de Vinyasa Flow online.', '2025-07-21 08:00:00'),
(9, 'Natação', 40, 'Nado livre na piscina do prédio.', '2025-07-21 20:00:00'),
(1, 'Corrida', 25, 'Trote leve antes do trabalho.', '2025-07-22 06:30:00'),
(3, 'Funcional', 55, 'Treino funcional na academia.', '2025-07-22 07:00:00'),
(5, 'Bicicleta', 60, 'Passeio de bicicleta na orla.', '2025-07-22 08:15:00'),
(8, 'Musculação', 70, 'Treino de costas e bíceps.', '2025-07-22 09:00:00'),
(10, 'Futebol', 90, 'Jogo com amigos.', '2025-07-21 20:30:00');

INSERT INTO hidratacao (id_usuario, quantidade_ml, data_hidratacao) VALUES
(1, 300, '2025-07-22 08:00:00'),
(1, 250, '2025-07-22 09:30:00'),
(2, 500, '2025-07-22 08:10:00'),
(3, 200, '2025-07-22 08:30:00'),
(4, 350, '2025-07-22 09:00:00'),
(5, 400, '2025-07-22 09:15:00'),
(1, 300, '2025-07-22 10:45:00'),
(2, 500, '2025-07-22 10:50:00'),
(6, 250, '2025-07-22 09:40:00'),
(7, 300, '2025-07-22 10:00:00');

INSERT INTO refeicao (id_usuario, tipo_refeicao, descricao_refeicao, foto_refeicao, data_refeicao) VALUES
(1, 'Café da manhã', 'Tapioca com queijo e café preto.', NULL, '2025-07-21 08:00:00'),
(2, 'Almoço', 'Frango grelhado, arroz integral, feijão e salada de alface e tomate.', NULL, '2025-07-21 12:30:00'),
(3, 'Jantar', 'Sopa de legumes com croutons.', NULL, '2025-07-21 20:00:00'),
(4, 'Lanche', 'Maçã e um punhado de castanhas.', NULL, '2025-07-21 16:00:00'),
(5, 'Café da manhã', 'Pão integral na chapa com ovos mexidos.', 'https://example.com/foto/ovos.jpg', '2025-07-22 07:30:00'),
(6, 'Almoço', 'Baião de dois com carne de sol e macaxeira frita.', NULL, '2025-07-22 13:00:00'),
(7, 'Lanche da tarde', 'Iogurte natural com granola e mel.', NULL, '2025-07-22 16:30:00'),
(8, 'Jantar', 'Salada Caesar com tiras de frango.', NULL, '2025-07-22 20:30:00'),
(9, 'Café da manhã', 'Vitamina de banana com aveia.', NULL, '2025-07-22 08:45:00'),
(10, 'Almoço', 'Feijoada completa.', NULL, '2025-07-20 14:00:00');

INSERT INTO meta (id_usuario, tipo_meta, valor_meta, unidade_meta, data_meta) VALUES
(1, 'Hidratação Diária', 3000, 'ml', '2025-07-22'),
(2, 'Passos Diários', 10000, 'passos', '2025-07-22'),
(3, 'Horas de Sono', 8, 'horas', '2025-07-22'),
(4, 'Correr', 5, 'km', '2025-07-25'),
(5, 'Meditar', 15, 'minutos', '2025-07-22'),
(1, 'Ler', 20, 'páginas', '2025-07-22'),
(7, 'Frequência de Exercícios', 4, 'vezes/semana', '2025-07-28'),
(8, 'Evitar Açúcar', 1, 'dia', '2025-07-23'),
(9, 'Nadar', 1500, 'metros', '2025-07-24'),
(10, 'Calorias', 2500, 'kcal', '2025-07-22');
