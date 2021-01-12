## Pre-reqs
- Python 3.8

## Installation
```
$python3.8 -m venv _venv
$. _venv/bin/activate
(_venv)$pip install -r requirements.txt
```

## Running
```
(_venv)$uvicorn core:app
```

## Data Files
- There are three users stored in 'database.txt'
- There are two users logged in, and their sessions are stored in 'sessions.txt'


## Logged In User
```
{
    "username": "jet-setter",
    "password": "r0u7!nG"
},
{
    "username": "lmb",
    "password": "null"
}

```



## API References
```
http://localhost:8000/docs
```
