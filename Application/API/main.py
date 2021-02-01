from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from routers import users

app = FastAPI(title="Book Recommendations")
app.include_router(users.router)

# templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.get('/', response_class=HTMLResponse)
# async def get_func():
#     """
#     Serves the main form page.
#     :return:
#     """
#     with open('./templates/bare template.html', 'rt') as fopen:
#         return fopen.read()


if __name__ == '__main__':
    import uvicorn

    from configparser import ConfigParser
    config = ConfigParser()
    config.read('/run/secrets/secrets.cfg')
    print(config['JWT']['SECRET_KEY'])

    uvicorn.run("main:app", host='0.0.0.0', port=3000, reload=True)
