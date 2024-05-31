CREATE TABLE users(
    id_user SERIAL PRIMARY KEY,
    username VARCHAR(20) NOT NULL,
    language VARCHAR(20) NOT NULL CHECK (language IN ('ru', 'en'))
);

CREATE TABLE achievements(
    id_achievement SERIAL PRIMARY KEY,
    achievement_name VARCHAR(40) NOT NULL,
    scores INTEGER NOT NULL,
	description VARCHAR(100) NOT NULL
);

CREATE TABLE users_and_their_achievements(
    id SERIAL PRIMARY KEY,
    id_user INTEGER NOT NULL,
    id_achievement INTEGER NOT NULL,
    date DATE NOT NULL DEFAULT (CURRENT_DATE),
    UNIQUE (id_user, id_achievement),
    FOREIGN KEY (id_user) REFERENCES users (id_user),
    FOREIGN KEY (id_achievement) REFERENCES achievements (id_achievement)
);

insert into users (username, language) VALUES
('rytee20', 'ru'),
('viki', 'ru'),
('PoliNa', 'ru'),
('axel', 'en'),
('HermitTheFrog', 'en');

insert into achievements (achievement_name, scores, description) VALUES
('Завсегдатай I', 10, 'Зайти на сайт 7 дней подряд'),
('Завсегдатай II', 20, 'Зайти на сайт 30 дней подряд'),
('Завсегдатай III', 30, 'Зайти на сайт 90 дней подряд'),
('Ветеран I', 10, '30 дней на сайте'),
('Ветеран II', 20, '150 дней на сайте'),
('Ветеран III', 30, '365 дней на сайте'),
('Любимчик I', 5, 'Получить 10 лайков на пост'),
('Любимчик II', 10, 'Получить 100 лайков на пост'),
('Любимчик III', 20, 'Получить 500 лайков на пост'),
('Любимчик IIII', 30, 'Получить 1000 лайков на пост'),
('Мастер комментария I', 5, 'Получить 10 лайков на комментарий'),
('Мастер комментария II', 10, 'Получить 100 лайков на комментарий'),
('Мастер комментария III', 20, 'Получить 500 лайков на комментарий'),
('Мастер комментария IIII', 30, 'Получить 1000 лайков на комментарий'),
('С первым днем', 5, 'Первый день на сайте'),
('Новичок', 10, 'Опубликовать первый пост'),
('Первая любовь', 10, 'Получить первый лайк на пост'),
('Со своим мнением', 10, 'Написать первый комментарий'),
('Родственные души', 10, 'Получить первый лайк на комментарий');

insert into users_and_their_achievements (id_user, id_achievement, date) VALUES
(1, 15, '2024-01-17'),
(1, 1, '2024-01-23'),
(1, 18, '2024-03-14'),
(1, 19, '2024-03-14'),
(1, 4, '2024-02-16'),

(2, 15, '2024-05-29'),
(2, 16, '2024-05-30'),
(2, 17, '2024-05-30'),
(2, 7, '2024-05-01'),
(2, 8, '2024-05-02'),
(2, 18, '2024-05-03'),
(2, 19, '2024-05-04'),
(2, 11, '2024-05-04'),
(2, 1, '2024-05-06'),

(3, 15, '2023-10-23'),
(3, 18, '2023-11-21'),
(3, 11, '2023-11-30'),
(3, 16, '2024-03-04'),
(3, 17, '2024-03-04'),
(3, 7, '2024-03-04'),
(3, 8, '2024-04-08'),
(3, 1, '2023-11-11'),
(3, 2, '2023-01-13'),
(3, 4, '2023-11-22'),
(3, 5, '2024-03-23'),

(4, 15, '2022-01-28'),
(4, 1, '2022-02-15'),
(4, 2, '2022-07-29'),
(4, 3, '2023-09-12'),
(4, 4, '2022-02-27'),
(4, 5, '2022-07-27'),
(4, 6, '2023-01-28'),

(5, 15, '2024-05-06');