import json

from fastapi import FastAPI, HTTPException, status, Request
from starlette.responses import JSONResponse, Response
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from passlib.hash import pbkdf2_sha256

app = FastAPI()

# models
class NewUser(BaseModel):
    username: str
    full_name: str
    password: str
    search_engine: str


class UserOut(BaseModel):
    username: str
    full_name: str
    search_engine: str


class Login(BaseModel):
    username: str
    password: str


@app.post("/user/create")
async def create_user(new_user: NewUser):
    # check if username in database file
    with open('database.txt', 'r') as db_file:
        users = db_file.readlines()

        for user in users:
            if new_user.username in user:
                raise HTTPException(
                    status_code=400,
                    detail="Username is already in used"
                )

    # hash password + salt
    # TODO: add salt
    hashed_password = pbkdf2_sha256.hash(new_user.password)

    # replace password with hashed password
    new_user.password = hashed_password

    # convert model to json
    to_json = jsonable_encoder(new_user)

    # write data to a text file
    with open('database.txt', 'a') as db_file:
      json.dump(to_json, db_file)
      db_file.write('\n')

    data = {'detail': 'User is created!'}

    response = JSONResponse(
        content=data,
        status_code=201
    )

    return response


@app.post("/login")
async def login_basic(login_info: Login):
    # check if user in database
    with open('database.txt', 'r') as db_file:
        users = db_file.readlines()

        for user in users:
            # convert str to json obj
            user_obj = json.loads(user)
            if(login_info.username in user_obj['username']
                    and pbkdf2_sha256.verify(login_info.password, user_obj['password'])):

                response = create_cookie(user_obj)
                return response

    raise HTTPException(
        status_code=400,
        detail="Incorrect username or password"
    )


@app.get("/user", response_model=UserOut)
async def get_user_data(session_id):
    username = ''

    if not session_id:
        return {"detail": "Empty session id"}

    # check session is created for the user
    with open('session.txt', 'r') as session_file:
        sessions = session_file.readlines()

        for session in sessions:
            # convert str to json obj
            session_obj = json.loads(session)
            if(session_id in session_obj['session']):
                username = session_obj['username']

    if not username:
        return {"detail": "Invalid session"}

    # search user in db and return it
    with open('database.txt', 'r') as db_file:
        users = db_file.readlines()

        for user in users:
            # convert str to json obj
            user_obj = json.loads(user)
            if username in user_obj['username']:
                # return in UserOut model
                return user_obj


@app.get("/logout")
async def logout(session_id):
    if not session_id:
        return {"detail": "Empty session id"}

    updated_sessions = []
    session_key = ''
    # check session is created for the user
    with open('session.txt', 'r') as session_file:
        sessions = session_file.readlines()

        for idx in range(len(sessions)):
            # convert str to json obj
            session_obj = json.loads(sessions[idx])
            if(session_id in session_obj['session']):
                session_key = session_obj['username']
                sessions.pop(idx)
                updated_sessions = sessions
    
    with open('session.txt', 'w+') as session_file:
        for session in updated_sessions:
            session_file.write(session)
            session_file.write('\n')
    
    content = {"detail": "Logout success"}
    response = JSONResponse(content=content, status_code=200)

    response.delete_cookie(session_key)
    return response

# helper method
def create_cookie(user):
    # session flag
    is_found = False

    # create session value for login user
    session_str = user['username'] + user['search_engine']
    hashed_session = pbkdf2_sha256.hash(session_str)

    data = {
        'username': user['username'],
        'session': hashed_session
    }

    # check if session is created for the user
    with open('session.txt', 'r') as session_file:
        sessions = session_file.readlines()

        for session in sessions:
            # convert str to json obj
            session_obj = json.loads(session)
            if(user['username'] in session_obj['username']):
                is_found = True
                break
        
    # write session info to a text file if not found
    if not is_found:
        with open('session.txt', 'a') as session_file:
          json.dump(data, session_file)
          session_file.write('\n')

    content = {'detail': 'Login success'}

    response = JSONResponse(
        content=content,
        status_code=200
    )

    # session cookie settings
    response.set_cookie(
        key=user['username'],
        value=hashed_session,
        secure=True,
        max_age=1800,
        expires=1800,
    )
    return response