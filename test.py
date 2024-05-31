import pytest
from fastapi.testclient import TestClient
from app.main import app, get_db
from sqlalchemy.orm import Session

client = TestClient(app)

# Тест для /users_achievements/users/{id_user}
def test_get_user():
    response = client.get("/users_achievements/users/1")
    assert response.status_code == 200
    assert response.json() == {"id_user": 1, "username": "rytee20", "language": "ru"}

def test_get_non_user():
    response = client.get("/users_achievements/users/6")
    assert response.status_code == 404

# Тест для /users_achievements/achievements
def test_get_all_achievements():
    response = client.get("/users_achievements/achievements")
    assert response.status_code == 200
    assert len(response.json()) > 0

# Тест для /users_achievements/users/{id_user}/achievements
def test_get_users_achievements():
    response = client.get("/users_achievements/users/1/achievements")
    assert response.status_code == 200
    assert response.json() == [
    {
        "id_achievement": 1,
        "achievement_name": "Завсегдатай I",
        "scores": 10,
        "description": "Зайти на сайт 7 дней подряд"
    },
    {
        "id_achievement": 4,
        "achievement_name": "Ветеран I",
        "scores": 10,
        "description": "30 дней на сайте"
    },
    {
        "id_achievement": 15,
        "achievement_name": "С первым днем",
        "scores": 5,
        "description": "Первый день на сайте"
    },
    {
        "id_achievement": 18,
        "achievement_name": "Со своим мнением",
        "scores": 10,
        "description": "Написать первый комментарий"
    },
    {
        "id_achievement": 19,
        "achievement_name": "Родственные души",
        "scores": 10,
        "description": "Получить первый лайк на комментарий"
    }
]

def test_get_non_users_achievements():
    response = client.get("/users_achievements/users/6/achievements")
    assert response.status_code == 404

# Тест для /users_achievements/users_with_max_achievements
def test_get_users_with_max_achievements():
    response = client.get("/users_achievements/users_with_max_achievements")
    assert response.status_code == 200
    assert response.json() == [{"id_user": 3, "username": "PoliNa", "count_achievements": 11}]

# Тест для /users_achievements/users_with_max_scores
def test_get_users_with_max_scores():
    response = client.get("/users_achievements/users_with_max_scores")
    assert response.status_code == 200
    assert response.json() == {"id_user": 4, "username": "axel", "total_scores": 125}

# Тест для /users_achievements/users_with_max_difference
def test_get_users_with_max_scores():
    response = client.get("/users_achievements/users_with_max_difference")
    assert response.status_code == 200
    assert response.json() == [
        {
            "difference": 120
        },
        {
            "id_user": 4,
            "username": "axel",
            "total_scores": 125
        },
        {
            "id_user": 5,
            "username": "HermitTheFrog",
            "total_scores": 5
        }
    ]

# Тест для /users_achievements/users_with_min_difference
def test_get_users_with_min_difference():
    response = client.get("/users_achievements/users_with_min_difference")
    assert response.status_code == 200
    assert response.json() == [
        {
            "difference": 10
        },
        {
            "id_user": 4,
            "username": "axel",
            "total_scores": 125
        },
        {
            "id_user": 3,
            "username": "PoliNa",
            "total_scores": 115
        }
    ]

# Тест для /users_achievements/users_with_7days_achievements
def test_get_users_with_7days_achievements():
    response = client.get("/users_achievements/users_with_7days_achievements")
    assert response.status_code == 404