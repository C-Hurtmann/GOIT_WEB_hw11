from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
import uvicorn

from src.database.db import redis_session
from src.routes import contacts
from src.routes import auth
from src.routes import users


origins = [
    'http://localhost:3000'
]

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')
app.include_router(users.router, prefix='/api')

@app.on_event('startup')
async def startup():
    """
    Start with app. Test redis connection. Init Fastapi limiter.
    """
    await redis_session.ping()
    await FastAPILimiter.init(redis_session)

@app.get('/')
def main():
    """
    Retrieve 'Welcome' message.
    
    :return: Message dict.
    """
    return {'message': 'Welcome'}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)