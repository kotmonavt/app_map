import os
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi import FastAPI
from gotrue.errors import AuthApiError
from pydantic import BaseModel
from math import *

load_dotenv()

url: str = "https://dxbgcjyicfxyhizutaiz.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR4YmdjanlpY2Z4eWhpenV0YWl6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTc4NjgzMTEsImV4cCI6MjAzMzQ0NDMxMX0.OpGnfFvMsHO56MyUspLmnFpVnRHFuxIqbemJpnMUYQE"
supabase: Client = create_client(url, key)

app = FastAPI()


@app.get("/")
async def home():
    return {"data": "based"}


class User(BaseModel):
    login: str
    password: str 


class warningZone(BaseModel):
    xCoord: float
    yCoord: float
    typeZone: str
    distance: float


class userPosition(BaseModel):
    xCoord: float
    yCoord: float


# Регистрация пользователя
@app.post("/users/sign-up")
async def create_user(user: User):
    
    credentials = {
    "email": user.login,
    "password": user.password
    }
    
    # TODO добавить обработку различных исключение при регистрации
    try:
        user, session = supabase.auth.sign_up(credentials)
    except AuthApiError as e:
        return AuthApiError.to_dict(e)

    res = {'status': 200,
           'user': user[1]}
    

    return res


@app.post("/users/sign-out")
async def log_out():
    res = supabase.auth.sign_out()

    return {"status": 200}


# Вход пользователя
@app.post("/users/sign-in")
async def get_user(user: User):

    credentials = {
    "email": user.login,
    "password": user.password
    }

    # TODO добавить обработку различных исключение при входе пользователя
    try:
        user, session = supabase.auth.sign_in_with_password(credentials)
    except AuthApiError as e:
        return AuthApiError.to_dict(e)

    res = {'status': 200,
           'user': user[1]}

    return res


# добавление записи об опасной зоне
@app.post("/warningZone/add")
async def addWarningZone(warningZone: warningZone):
    data = supabase.table("warningZone").insert({"xCoord": warningZone.xCoord, "yCoord": warningZone.yCoord, "typeZone": warningZone.typeZone, "distance": warningZone.distance}).execute()
    assert len(data.data) > 0
    x_p = warningZone.xCoord + warningZone.distance
    x_m = warningZone.xCoord - warningZone.distance
    y_p = warningZone.yCoord + warningZone.distance
    y_m = warningZone.yCoord - warningZone.distance
    data_coord = supabase.table('coord').insert({"id_coord": data.data[0]['id'],"x_p": x_p, "x_m": x_m, "y_p": y_p, "y_m": y_m}).execute()
    assert len(data_coord.data) > 0


    # продумать варианты ошибок и ответы на них


@app.post("/warningZone/get")
async def getWarningZone(userPosition: userPosition):
    data = supabase.table('coord').select('id_coord', count='exact').filter('x_p', 'gte', userPosition.xCoord).filter('x_m', 'lte', userPosition.xCoord).filter('y_p', 'gte', userPosition.yCoord).filter('y_m', 'lte', userPosition.yCoord).execute()
    if data.count > 0:
        count = data.count
        data_responce = ''
        for i in range(0, count):
            data_ = supabase.table('warningZone').select('*').filter('id', 'eq', data.data[0]['id_coord']).execute()
            if i == 0:
                data_responce = data_
            else:
                data_responce = data_responce + ' ' + data_
        return data_responce
    else:
        res = {'status': 200}
        return res
