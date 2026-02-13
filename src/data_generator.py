import random
import json
from datetime import datetime, timedelta


class MovieDataGenerator:
    def __init__(self):
        self.genres = [
            "Драма", "Комедия", "Боевик", "Триллер", "Ужасы",
            "Фантастика", "Мелодрама", "Детектив", "Приключения",
            "Фэнтези", "Криминал", "Мистика", "Вестерн", "Мюзикл"
        ]

        self.movie_titles = [
            ("Побег из Шоушенка", "Драма", 1994),
            ("Крестный отец", "Криминал", 1972),
            ("Темный рыцарь", "Боевик", 2008),
            ("Криминальное чтиво", "Криминал", 1994),
            ("Властелин колец", "Фэнтези", 2001),
            ("Зеленая миля", "Драма", 1999),
            ("Форрест Гамп", "Драма", 1994),
            ("Начало", "Фантастика", 2010),
            ("Матрица", "Фантастика", 1999),
            ("Интерстеллар", "Фантастика", 2014),
            ("Гладиатор", "Боевик", 2000),
            ("Король Лев", "Мультфильм", 1994),
            ("Титаник", "Мелодрама", 1997),
            ("Молчание ягнят", "Триллер", 1991),
            ("Бойцовский клуб", "Триллер", 1999),
            ("Хороший, плохой, злой", "Вестерн", 1966),
            ("Психо", "Ужасы", 1960),
            ("Сияние", "Ужасы", 1980),
            ("Назад в будущее", "Фантастика", 1985),
            ("Терминатор", "Боевик", 1984),
            ("Чужой", "Ужасы", 1979),
            ("Хищник", "Боевик", 1987),
            ("Основной инстинкт", "Триллер", 1992),
            ("Семь", "Триллер", 1995),
            ("Джокер", "Драма", 2019),
            ("Остров проклятых", "Триллер", 2010),
            ("Дюна", "Фантастика", 2021),
            ("Довод", "Фантастика", 2020),
            ("Аватар", "Фантастика", 2009),
            ("Мстители", "Боевик", 2012)
        ]

    def generate_movies(self, count=100):
        movies = []

        for title, main_genre, year in self.movie_titles:
            movie = self._create_movie(title, main_genre, year)
            movies.append(movie)

        while len(movies) < count:
            movie = self._create_random_movie()
            movies.append(movie)

        random.shuffle(movies)

        for i, movie in enumerate(movies):
            movie["id"] = i + 1

        return movies

    def _create_movie(self, title, main_genre, year):
        movie_genres = [main_genre]
        additional_genres = random.sample([g for g in self.genres if g != main_genre],
                                          random.randint(0, 2))
        movie_genres.extend(additional_genres)

        descriptions = [
            f"Захватывающий {main_genre.lower()} о невероятных событиях, которые изменят ваше представление о кино.",
            f"{main_genre} высшей пробы с блестящей игрой актеров и неожиданной развязкой.",
            f"История, которая заставит вас смеяться и плакать. Настоящий шедевр {main_genre.lower()}.",
            f"Эпическое путешествие в мир приключений и опасностей. Обязателен к просмотру!",
            f"Фильм, который держит в напряжении от первой до последней минуты.",
            f"Трогательная история о любви, дружбе и предательстве в жанре {main_genre.lower()}.",
            f"Зрелищный блокбастер с невероятными спецэффектами и захватывающим сюжетом.",
            f"Философская притча, замаскированная под {main_genre.lower()}."
        ]

        return {
            "title": title,
            "original_title": title,
            "overview": random.choice(descriptions),
            "genres": movie_genres,
            "year": year,
            "release_date": f"{year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "vote_average": round(random.uniform(6.5, 9.2), 1),
            "vote_count": random.randint(1000, 500000),
            "popularity": round(random.uniform(50, 950), 1),
            "runtime": random.choice([90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 150]),
            "director": random.choice(["Кристофер Нолан", "Квентин Тарантино", "Мартин Скорсезе",
                                       "Стивен Спилберг", "Дэвид Финчер", "Ридли Скотт",
                                       "Джеймс Кэмерон", "Питер Джексон", "Дени Вильнёв"]),
            "cast": random.sample([
                "Леонардо ДиКаприо", "Брэд Питт", "Том Хэнкс", "Роберт Де Ниро",
                "Аль Пачино", "Морган Фриман", "Киану Ривз", "Мэтт Дэймон",
                "Кристиан Бэйл", "Хит Леджер", "Хоакин Феникс", "Джонни Депп"
            ], 5)
        }

    def _create_random_movie(self):
        year = random.randint(1970, 2024)
        main_genre = random.choice(self.genres)

        title_parts = [
            f"{random.choice(['Тайна', 'Легенда', 'История', 'Путь', 'Сила'])} "
            f"{random.choice(['воина', 'меча', 'крови', 'тьмы', 'света'])}",
            f"{random.choice(['Последний', 'Великий', 'Темный', 'Безумный'])} "
            f"{random.choice(['герой', 'воин', 'охотник', 'странник'])}",
            f"{random.choice(['Город', 'Земля', 'Мир', 'Остров'])} "
            f"{random.choice(['грехов', 'теней', 'мечты', 'забвения'])}"
        ]

        title = random.choice(title_parts)

        return self._create_movie(title, main_genre, year)


generator = MovieDataGenerator()