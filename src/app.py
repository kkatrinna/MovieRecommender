from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from typing import Optional, List
import uvicorn
import json
import random

from data_generator import generator
from recommender import recommender

movies = []
genres = generator.genres


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "=" * 50)
    print("🎬 MovieRecommender запускается...")
    print("=" * 50)

    global movies
    try:
        movies = generator.generate_movies(50)
        print(f"✅ Сгенерировано {len(movies)} фильмов")

        recommender.load_movies(movies)
        if recommender.build_model():
            print("✅ ML модель построена успешно")
        else:
            print("⚠️ Модель не построена (недостаточно данных)")

        print("✨ Приложение готово к работе!")

    except Exception as e:
        print(f"❌ Ошибка при инициализации: {e}")

    print("=" * 50 + "\n")

    yield
    print("\n" + "=" * 50)
    print("👋 Остановка приложения...")
    print("=" * 50 + "\n")


app = FastAPI(
    title="MovieRecommender",
    description="🎬 AI рекомендации фильмов без внешних API",
    version="2.0.0",
    lifespan=lifespan
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    global movies

    if not movies:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "popular": [],
            "top_rated": [],
            "recent": [],
            "genres": genres,
            "error": "Данные еще загружаются..."
        })

    popular = sorted(movies, key=lambda x: x['popularity'], reverse=True)[:12]
    top_rated = sorted(movies, key=lambda x: x['vote_average'], reverse=True)[:12]
    recent = sorted([m for m in movies if m['year'] >= 2020],
                    key=lambda x: x['year'], reverse=True)[:12]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "popular": popular,
        "top_rated": top_rated,
        "recent": recent,
        "genres": genres
    })


@app.get("/movie/{movie_id}", response_class=HTMLResponse)
async def movie_detail(request: Request, movie_id: int):
    global movies

    movie = next((m for m in movies if m['id'] == movie_id), None)
    if not movie:
        return RedirectResponse(url="/", status_code=302)

    similar = recommender.get_recommendations_by_movie(movie_id, 8)

    return templates.TemplateResponse("movie.html", {
        "request": request,
        "movie": movie,
        "similar": similar,
        "genres": genres
    })


@app.get("/genre/{genre}", response_class=HTMLResponse)
async def genre_page(request: Request, genre: str):
    global movies

    genre_movies = [m for m in movies if genre in m['genres']]
    genre_movies = sorted(genre_movies,
                          key=lambda x: x['vote_average'],
                          reverse=True)

    return templates.TemplateResponse("genre.html", {
        "request": request,
        "genre": genre,
        "movies": genre_movies
    })


@app.get("/recommendations", response_class=HTMLResponse)
async def recommendations_page(request: Request):
    global movies

    popular_recs = recommender.get_popular_recommendations(12)
    drama_recs = recommender.get_recommendations_by_genre("Драма", 8)
    action_recs = recommender.get_recommendations_by_genre("Боевик", 8)

    return templates.TemplateResponse("recommendations.html", {
        "request": request,
        "popular": popular_recs,
        "drama": drama_recs,
        "action": action_recs,
        "genres": genres
    })


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = ""):
    global movies

    if q and movies:
        q_lower = q.lower()
        results = [
            m for m in movies
            if q_lower in m['title'].lower() or
               q_lower in m['overview'].lower() or
               any(q_lower in g.lower() for g in m['genres'])
        ]
    else:
        results = []

    return templates.TemplateResponse("search.html", {
        "request": request,
        "query": q,
        "results": results
    })


@app.get("/api/status")
async def api_status():
    return {
        "status": "ok",
        "movies_count": len(movies),
        "genres": genres,
        "version": "2.0.0"
    }


@app.get("/api/movies")
async def api_movies(page: int = 1, per_page: int = 20):
    global movies

    start = (page - 1) * per_page
    end = start + per_page

    return {
        "page": page,
        "per_page": per_page,
        "total": len(movies),
        "movies": movies[start:end]
    }


@app.get("/api/movies/{movie_id}")
async def api_movie_detail(movie_id: int):
    global movies

    movie = next((m for m in movies if m['id'] == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")

    return movie


@app.get("/api/similar/{movie_id}")
async def api_similar(movie_id: int, n: int = 8):
    similar = recommender.get_recommendations_by_movie(movie_id, n)
    return {"similar": similar}


@app.get("/api/recommendations/popular")
async def api_popular():
    popular = recommender.get_popular_recommendations(20)
    return {"recommendations": popular}


@app.get("/api/recommendations/genre/{genre}")
async def api_genre(genre: str):
    recs = recommender.get_recommendations_by_genre(genre, 20)
    return {"recommendations": recs}


@app.post("/api/personalized")
async def api_personalized(ratings: dict):
    recs = recommender.get_personalized_recommendations(ratings, 20)
    return {"recommendations": recs}


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🚀 Запуск сервера...")
    print("📡 http://localhost:8000")
    print("📚 Документация: http://localhost:8000/docs")
    print("=" * 50 + "\n")

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )