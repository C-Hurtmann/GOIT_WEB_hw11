from redis.asyncio import Redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
import uvicorn

from src.routes import contacts
from src.routes import auth
from src.conf.config import settings

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

@app.on_event('startup')
async def startup():
    r = Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding='utf-8', decode_responses=True)
    await FastAPILimiter.init(r)

@app.get('/')
def main():
    return {'message': 'Welcome'}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)