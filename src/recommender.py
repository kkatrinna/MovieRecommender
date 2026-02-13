import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
import pickle
import os
from typing import List, Dict


class MovieRecommender:
    def __init__(self):
        self.movies_df = None
        self.similarity_matrix = None
        self.tfidf_vectorizer = None

    def load_movies(self, movies: List[Dict]):
        self.movies_df = pd.DataFrame(movies)

        self.movies_df['features'] = (
                self.movies_df['title'] + ' ' +
                self.movies_df['overview'] + ' ' +
                self.movies_df['genres'].apply(lambda x: ' '.join(x)) + ' ' +
                self.movies_df['director'] + ' ' +
                self.movies_df['cast'].apply(lambda x: ' '.join(x[:3]))
        )

        print(f"✅ Загружено {len(self.movies_df)} фильмов")
        return self.movies_df

    def build_model(self):
        if self.movies_df is None or len(self.movies_df) < 2:
            print("❌ Недостаточно данных")
            return False

        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )

        tfidf_matrix = self.tfidf_vectorizer.fit_transform(
            self.movies_df['features'].fillna('')
        )

        self.similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

        print(f"✅ Модель построена. Матрица: {self.similarity_matrix.shape}")
        return True

    def get_recommendations_by_movie(self, movie_id: int, n_recommendations: int = 10) -> List[Dict]:

        if self.similarity_matrix is None:
            return self.get_popular_recommendations(n_recommendations)

        movie_indices = self.movies_df[self.movies_df['id'] == movie_id].index
        if len(movie_indices) == 0:
            return self.get_popular_recommendations(n_recommendations)

        idx = movie_indices[0]

        sim_scores = list(enumerate(self.similarity_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        sim_scores = sim_scores[1:n_recommendations + 1]
        movie_indices = [i[0] for i in sim_scores]
        similarity_scores = [i[1] for i in sim_scores]

        recommendations = self.movies_df.iloc[movie_indices].to_dict('records')

        for rec, score in zip(recommendations, similarity_scores):
            rec['similarity'] = round(score * 100, 1)

        return recommendations

    def get_recommendations_by_genre(self, genre: str, n_recommendations: int = 10) -> List[Dict]:

        if self.movies_df is None:
            return []

        genre_movies = self.movies_df[
            self.movies_df['genres'].apply(lambda x: genre in x)
        ]

        genre_movies = genre_movies.sort_values(
            ['vote_average', 'popularity'],
            ascending=False
        ).head(n_recommendations)

        return genre_movies.to_dict('records')

    def get_popular_recommendations(self, n_recommendations: int = 10) -> List[Dict]:

        if self.movies_df is None:
            return []

        self.movies_df['popularity_score'] = (
                self.movies_df['popularity'] / self.movies_df['popularity'].max() * 0.3 +
                self.movies_df['vote_average'] / 10 * 0.7
        )

        popular = self.movies_df.sort_values(
            'popularity_score',
            ascending=False
        ).head(n_recommendations)

        return popular.to_dict('records')

    def get_recommendations_by_preferences(self, preferences: Dict, n_recommendations: int = 10) -> List[Dict]:

        if self.movies_df is None:
            return []

        filtered = self.movies_df.copy()

        if 'genres' in preferences and preferences['genres']:
            filtered = filtered[
                filtered['genres'].apply(
                    lambda x: any(g in x for g in preferences['genres'])
                )
            ]

        if 'min_rating' in preferences:
            filtered = filtered[filtered['vote_average'] >= preferences['min_rating']]

        if 'min_year' in preferences:
            filtered = filtered[filtered['year'] >= preferences['min_year']]
        if 'max_year' in preferences:
            filtered = filtered[filtered['year'] <= preferences['max_year']]

        filtered = filtered.sort_values(
            ['vote_average', 'popularity'],
            ascending=False
        ).head(n_recommendations)

        return filtered.to_dict('records')

    def get_personalized_recommendations(self, user_ratings: Dict[int, float], n_recommendations: int = 10) -> List[
        Dict]:
        if self.movies_df is None or not user_ratings:
            return self.get_popular_recommendations(n_recommendations)

        liked_movies = []
        for movie_id, rating in user_ratings.items():
            if rating >= 7:
                liked = self.movies_df[self.movies_df['id'] == movie_id]
                if not liked.empty:
                    liked_movies.append(liked.iloc[0])

        if not liked_movies:
            return self.get_popular_recommendations(n_recommendations)

        recommendations = []
        seen_ids = set(user_ratings.keys())

        for liked in liked_movies:
            similar = self.get_recommendations_by_movie(liked['id'], 5)
            for movie in similar:
                if movie['id'] not in seen_ids:
                    movie['recommendation_score'] = movie.get('similarity', 0) * (liked['vote_average'] / 10)
                    recommendations.append(movie)
                    seen_ids.add(movie['id'])

        unique_recs = {}
        for rec in recommendations:
            if rec['id'] not in unique_recs:
                unique_recs[rec['id']] = rec
            else:
                if rec.get('recommendation_score', 0) > unique_recs[rec['id']].get('recommendation_score', 0):
                    unique_recs[rec['id']] = rec

        sorted_recs = sorted(
            unique_recs.values(),
            key=lambda x: x.get('recommendation_score', 0),
            reverse=True
        )[:n_recommendations]

        return sorted_recs


recommender = MovieRecommender()