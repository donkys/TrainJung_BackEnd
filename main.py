from typing import List
import fastapi as _fastapi
import fastapi.security as _security
import uvicorn
import logging

import sqlalchemy.orm as _orm
import scraping_railway as railway

import services as _services
import schemas as _schemas

app = _fastapi.FastAPI(
    title="Train-Jung",
    version=0.1,
    root_path="/"
  )

_services.create_database()

@app.post("/api/users")
async def create_user(
    user: _schemas.UserCreate, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    db_user = await _services.get_user_by_email(user.email, db)
    if db_user:
        raise _fastapi.HTTPException(
            status_code=400, detail="Email already in use")

    user = await _services.create_user(user, db)

    return await _services.create_token(user)


@app.post("/api/token")
async def generate_token(
    form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    user = await _services.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise _fastapi.HTTPException(
            status_code=401, detail="Invalid Credentials")

    return await _services.create_token(user)

@app.get("/api/users/me", response_model=_schemas.User)
async def get_user(user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    return user

# get all train {number, name, time(array)}
@app.get("/allTrainByStation")
async def allTrainByStation():
    return railway._getTrainNumber()

# get all train {number, name, time(array)}
@app.get("/allTrainNumber")
async def allTrainByNumber():
    return railway._getTrain()

# get all train {number, name, time(array)}
@app.get("/allStationAtoB/{A}/{B}")
async def StationAtoB(A: int, B: int):
    return railway._getStationAtoB(A, B)

# get all train {number, name, time}
@app.get("/train/{trainID}")
async def train(trainID: int):
    return railway._getTrainByID(trainID)

@app.get("/Table/{trainID}")
async def getTableTrainBy(trainID: int):
    return railway._getTableTrainByID(trainID) 

logger = logging.getLogger("uvicorn.error")