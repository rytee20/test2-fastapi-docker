from enum import Enum
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from app import models
from app import database
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from mtranslate import translate as mtranslate
from sqlalchemy import func
from sqlalchemy import case

app=FastAPI()
models.database.Base.metadata.create_all(bind=database.engine)

# Таблица с данными о пользователях
class UsersBase(BaseModel):
    id_user: int                            # Идентификатор
    username: str                           # Имя пользователя
    language: str                           # Язык

# Таблица достижений
class AchievementsBase(BaseModel):
    id_achievement: int                     # Идентиффикатор
    achievement_name: str                   # Наименование достижения
    scores: int                             # Количество очков
    description: str                        # Описание достижения

# Таблица выдачи достижений пользователям
class UsersAchievementsBase(BaseModel):
    id: int                                 # Идентификато
    id_user: List[UsersBase]                # Идентификатор пользователя
    id_achievement: List[AchievementsBase]  # Идентификатор достижения
    date: datetime                          # Дата выдачи

# Предоставление поддерживаемых языков
class Language(str, Enum):
    ru = "ru" # Русский язык
    en = "en" # Английский язык

def get_db():
    db=database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Предоставление данных о пользователе
@app.get("/users_achievements/users/{id_user}")
async def get_user(id_user: int, db: Session = Depends(get_db)):
    result = db.query(models.Users).filter(models.Users.id_user==id_user).first()

    if not result:
        raise HTTPException (status_code=404,detail='User is not found')
    
    return result

# Предоставление данных о всех возможных достижениях
@app.get("/users_achievements/achievements")
async def get_all_achievements(db: Session = Depends(get_db)):
    result = db.query(models.Achievements).all()

    if not result:
        raise HTTPException (status_code=404,detail='Achievements is not found')
    
    return result

# Предоставления данных о достижения конкретного пользователя на его языке
@app.get("/users_achievements/users/{id_user}/achievements")
async def get_users_achievements(id_user: int, db: Session = Depends(get_db)):
    #Достижения пользователя
    result = (db.query(models.Achievements)
              .join(models.Users_Achievements)
              .filter(models.Users_Achievements.id_user==id_user)
              .all())

    if not result:
        raise HTTPException (status_code=404,detail='Achievements is not found')

    # Данные пользователя
    user = db.query(models.Users).filter(models.Users.id_user == id_user).first()

    # Данные о достижениях с переводом на язык пользователя
    translated_achievements = []
    for achievement in result:
        translated_achievement = {
            "id_achievement": achievement.id_achievement,
            "achievement_name": mtranslate(achievement.achievement_name, user.language),
            "scores": achievement.scores,
            "description": mtranslate(achievement.description, user.language)
        }
        translated_achievements.append(translated_achievement)

    return translated_achievements

# Предоставление данных о пользователях с максимальным количеством достижений
@app.get("/users_achievements/users_with_max_achievements")
async def get_users_with_max_achievements(db: Session = Depends(get_db)):
    # Подсчет достижений каждого пользователя
    user_achievements_count = (db.query(models.Users_Achievements.id_user, func.count().label("achievements_count"))
                               .group_by(models.Users_Achievements.id_user)
                               .subquery())

    # Максимальное количество достижений
    max_achievements_count = db.query(func.max(user_achievements_count.c.achievements_count)).scalar()

    # Пользователи с количеством достижений равным максимальному
    users_with_max_achievements = (db.query(models.Users)
                                   .join(user_achievements_count, models.Users.id_user == user_achievements_count.c.id_user)
                                   .filter(user_achievements_count.c.achievements_count == max_achievements_count)
                                   .all())

    if not users_with_max_achievements:
        raise HTTPException (status_code=404,detail='Users is not found')

    result = []
    for user in users_with_max_achievements:
        r = {
            "id_user": user.id_user,
            "username": user.username,
            "count_achievements": max_achievements_count
        }
        result.append(r)

    return result

# Предоставление данных о пользователях с максимальным количеством очков
@app.get("/users_achievements/users_with_max_scores")
async def get_users_with_max_scores(db: Session = Depends(get_db)):
    # Подсчет очков каждого пользователя
    user_scores_count = (
        db.query(
            models.Users_Achievements.id_user,
            func.sum(models.Achievements.scores).label("total_scores"))
        .join(models.Achievements, models.Users_Achievements.id_achievement == models.Achievements.id_achievement)
        .group_by(models.Users_Achievements.id_user)
        .subquery())

    # Максимальное количество очков
    max_scores = db.query(func.max(user_scores_count.c.total_scores)).scalar()

    # Пользователи с количеством очков равным максимальному
    users_with_max_scors = db.query(models.Users).join(user_scores_count, models.Users.id_user == user_scores_count.c.id_user).filter(user_scores_count.c.total_scores == max_scores).all()

    if not users_with_max_scors:
        raise HTTPException (status_code=404,detail='Users is not found')
    
    result = []
    for user in users_with_max_scors:
        r = {
            "id_user": user.id_user,
            "username": user.username,
            "total_scores": max_scores
        }
        result.append(r)
    
    return result

# Предоставление данных о пользователях с максимальной разницей очков достижений
@app.get("/users_achievements/users_with_max_difference")
async def get_users_with_max_difference(db: Session = Depends(get_db)):
    # Подсчет очков каждого пользователя
    user_scores_count = (
        db.query(
            models.Users_Achievements.id_user,
            func.sum(models.Achievements.scores).label("total_scores")
            )
        .join(models.Achievements, models.Users_Achievements.id_achievement == models.Achievements.id_achievement)
        .group_by(models.Users_Achievements.id_user)
        .subquery()
        )

    # Максимальное количество очков
    max_scores = db.query(func.max(user_scores_count.c.total_scores)).scalar()

    # Пользователи с количеством очков равным максимальному
    users_with_max_scors = (
        db.query(models.Users.id_user, models.Users.username, user_scores_count.c.total_scores)
        .join(user_scores_count, models.Users.id_user == user_scores_count.c.id_user)
        .filter(user_scores_count.c.total_scores == max_scores)
        .all()
    )

    # Максимальное количество очков
    min_scores = db.query(func.min(user_scores_count.c.total_scores)).scalar()

    # Пользователи с количеством очков равным максимальному
    users_with_min_scors = (
        db.query(models.Users.id_user, models.Users.username, user_scores_count.c.total_scores)
        .join(user_scores_count, models.Users.id_user == user_scores_count.c.id_user)
        .filter(user_scores_count.c.total_scores == min_scores)
        .all()
    )

    if not users_with_max_scors and not users_with_min_scors:
        raise HTTPException (status_code=404,detail='Users is not found')

    result = [{"difference": max_scores-min_scores}]
    result += [{"id_user": id_user,  "username": username, "total_scores": total_scores} 
              for id_user, username, total_scores in users_with_max_scors]
    result += [{"id_user": id_user,  "username": username, "total_scores": total_scores} 
              for id_user, username, total_scores in users_with_min_scors]

    return result

# Предоставление данных о пользователях с минимальной разницей очков достижений
@app.get("/users_achievements/users_with_min_difference")
async def get_users_with_min_difference(db: Session = Depends(get_db)):
    # Подсчет очков каждого пользователя
    user_scores_count = (
        db.query(
            models.Users_Achievements.id_user,
            func.sum(models.Achievements.scores).label("total_scores")
        )
        .join(models.Achievements, models.Users_Achievements.id_achievement == models.Achievements.id_achievement)
        .group_by(models.Users_Achievements.id_user)
        .subquery()
    )
    
    user_scores_count2 = db.query(user_scores_count.c.id_user,user_scores_count.c.total_scores).all()

    # Преобразование результатов в список словарей
    user_scores_list = [{"id_user": id_user, "total_scores": total_scores} 
                          for id_user, total_scores in user_scores_count2]
    
    # Сортировка списка по total_scores
    sorted_user_scores_count2 = sorted(user_scores_list, key=lambda x: x["total_scores"])

    min_difference = float('inf')
    scores1 = -1
    scores2 = -1

    # Найти минимальную разницу total_scores
    for i in range(len(sorted_user_scores_count2) - 1):
        diff = sorted_user_scores_count2[i + 1]["total_scores"] - sorted_user_scores_count2[i]["total_scores"]
        if diff < min_difference and diff != 0:
            min_difference = diff
            scores1 = sorted_user_scores_count2[i + 1]["total_scores"]
            scores2 = sorted_user_scores_count2[i]["total_scores"]

    if scores1 == -1 and scores2 == -1:
        raise HTTPException(status_code=404, detail='Users not found')

    # Запрос для получения пользователей с указанными очками
    users1 = (
        db.query(models.Users.id_user, models.Users.username, user_scores_count.c.total_scores)
        .join(user_scores_count, models.Users.id_user == user_scores_count.c.id_user)
        .filter(user_scores_count.c.total_scores == scores1)
        .all()
    )

    users2 = (
        db.query(models.Users.id_user, models.Users.username, user_scores_count.c.total_scores)
        .join(user_scores_count, models.Users.id_user == user_scores_count.c.id_user)
        .filter(user_scores_count.c.total_scores == scores2)
        .all()
    )

    result = [{"difference": scores1 - scores2}]
    result += [{"id_user": id_user, "username": username, "total_scores": total_scores} 
               for id_user, username, total_scores in users1]
    result += [{"id_user": id_user, "username": username, "total_scores": total_scores} 
               for id_user, username, total_scores in users2]

    return result

# Предоставление данных о пользователях, которые за последние 7 дней каждый день получали хотя бы одно достижение
@app.get("/users_achievements/users_with_7days_achievements")
async def get_users_with_7days_achievements(db: Session = Depends(get_db)):
    # Текущая дата
    today_date = datetime.now()

    # Данные о пользователи и дате полученных ими достижений за последние 7 дней
    get_users_date_achievements = (
        db.query(
            models.Users_Achievements.id_user,
            func.date(models.Users_Achievements.date).label("date"))
        .filter(models.Users_Achievements.date >= today_date - timedelta(days=7))
        .filter(models.Users_Achievements.date <= today_date)
        .subquery())

    # Данные о пользователе и количестве полученных им достижений за каждый день в течении последней недели
    get_users_count_7days_achievements = (
        db.query(
            get_users_date_achievements.c.id_user,
            func.sum(case((func.date(get_users_date_achievements.c.date) == func.date(today_date - timedelta(days=6)), 1),else_ =0)).label("day1"),
            func.sum(case((func.date(get_users_date_achievements.c.date) == func.date(today_date - timedelta(days=5)), 1),else_ =0)).label("day2"),
            func.sum(case((func.date(get_users_date_achievements.c.date) == func.date(today_date - timedelta(days=4)), 1),else_ =0)).label("day3"),
            func.sum(case((func.date(get_users_date_achievements.c.date) == func.date(today_date - timedelta(days=3)), 1),else_ =0)).label("day4"),
            func.sum(case((func.date(get_users_date_achievements.c.date) == func.date(today_date - timedelta(days=2)), 1),else_ =0)).label("day5"),
            func.sum(case((func.date(get_users_date_achievements.c.date) == func.date(today_date - timedelta(days=1)), 1),else_ =0)).label("day6"),
            func.sum(case((func.date(get_users_date_achievements.c.date) == func.date(today_date), 1),else_ =0)).label("day7"),)
        
        .group_by(get_users_date_achievements.c.id_user)
        .all())
    
    get_users_count_7days_achievements_list = [{"id_user": id_user, "day1": day1, "day2": day2, "day3": day3, "day4": day4, "day5": day5, "day6": day6, "day7": day7} 
            for id_user, day1, day2, day3, day4, day5, day6, day7 in get_users_count_7days_achievements]
    
    result = []
    for user in get_users_count_7days_achievements_list:
        if(user.get("day1")!=0 and user.get("day2")!=0 and user.get("day3")!=0 and user.get("day4")!=0 and user.get("day5")!=0 and user.get("day6")!=0 and user.get("day7")!=0):
            r = {
                "id_user": user.get("id_user")
            }
            result.append(r)

    if not result:
        raise HTTPException (status_code=404,detail='Users is not found')

    return result

# Добавление достижения
@app.post("/users_achievements/achievements/create")
async def create_achievement(achievement_name:str, scores:int, description:str, db:Session = Depends(get_db)):
    db_achievement = models.Achievements(achievement_name=achievement_name, scores=scores, description=description)
    db.add(db_achievement)
    db.commit()
    db.refresh(db_achievement)

# Добавления нового пользователя
@app.post("/users_achievements/users/create")
async def create_user(username: str, language: Language, db: Session = Depends(get_db)):
    db_user = models.Users(username=username, language=language.value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

# Присвоение достижения пользователю
@app.post("/users_achievements/set_achievement")
async def set_achievement(id_user:int, id_achievement:int, db: Session = Depends(get_db)):
    # Проверяем есть ли у пользователя данное достижение
    user_with_such_achievement = (
        db.query(
            models.Users_Achievements.id_user,
            models.Users_Achievements.id_achievement)
        .filter(models.Users_Achievements.id_user==id_user)
        .filter(models.Users_Achievements.id_achievement==id_achievement)
        .all())
    
    if not user_with_such_achievement:
        db_u_a = models.Users_Achievements(id_user=id_user, id_achievement=id_achievement)
        db.add(db_u_a)
        db.commit()
        db.refresh(db_u_a)
    else: 
        raise HTTPException (status_code=409,detail='The user already has this achievement')
