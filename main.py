from redis.asyncio import Redis
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
import uvicorn

from src.routes import contacts
from src.routes import auth


app = FastAPI()

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')

@app.on_event('startup')
async def startup():
    r = Redis(host='localhost', port=6379, db=0, encoding='utf-8', decode_responses=True)
    await FastAPILimiter.init(r)

@app.get('/')
def main():
    return {'message': 'Welcome'}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)