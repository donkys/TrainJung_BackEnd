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

@app.get("/Station")
async def getMyStation(user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    return railway._getInfoStation(user.idStation)

@app.post("/updateTime")
async def updateTime(idStation: int, numberTrain: int, time: str = "", user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    if idStation != user.idStation:
        raise _fastapi.HTTPException(
            status_code=400, detail="not permission")

    return railway._updatetime(idStation,numberTrain, time)

@app.get("/api/users/me", response_model=_schemas.User)
async def get_user(user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    return user

@app.post("/Status")
async def addStatus(trainNumber: int, onTime: bool, message: str, user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    return railway._addStatus(user.idStation, trainNumber, onTime , message)

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

@app.get("/Table/{trainID}/{A}/{B}")
async def getTableTrainBy(trainID: int, A:int, B:int):
    return railway._getTableTrainByIDAtoB(trainID, A, B) 

@app.get("/Home")
async def getHome():
    return railway._home() 

@app.get("/NameOfTrain")
async def getKeyTrain():
    return railway._getNameTrain()

@app.get("/NameOfTrain2")
async def getKeyTrain2():
    return railway._getNameTrain2()

@app.get("/BookmarkALL")
async def bookmarkAll():
    return railway._bookmarkAll()

@app.get("/BookmarkAdd/{id}")
async def bookmarkAdd(id:int):
    return railway.__insertBookmark(id)

@app.get("/BookmarkDelete/{id}")
async def bookmarkDelete(id:int):
    return railway.__deleteBookmark(id)

@app.get("/Bookmark")
async def bookmark():
    return railway.__getBookmark()


logger = logging.getLogger("uvicorn.error")