import logging

from fastapi import FastAPI
import uvicorn
from uvicorn.logging import DefaultFormatter
from src.routes import contacts
from src.routes import auth


logger = logging.getLogger('uvicorn debug')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setFormatter(DefaultFormatter())
logger.addHandler(handler)

app = FastAPI()

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')

@app.get('/')
def main():
    logger.debug('hello')
    return {'message': 'Welcome'}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)