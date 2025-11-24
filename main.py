from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

SECRET_TOKEN = "szupertitkos-jelszo-123"
COOKIE_NAME = "media_access_token"


@app.middleware("http")
async def check_video_access(request: Request, call_next):
    path = request.url.path

    # Csak a /hls mappát védjük
    if path.startswith("/hls"):
        # Most a SÜTIKET (Cookies) ellenőrizzük, nem az URL-t
        token_in_cookie = request.cookies.get(COOKIE_NAME)

        if token_in_cookie != SECRET_TOKEN:
            return Response(content="Hozzáférés megtagadva! Érvénytelen vagy hiányzó süti.", status_code=403)

    response = await call_next(request)
    return response


app.mount("/hls", StaticFiles(directory="hls_output"), name="hls")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Rendereljük a HTML-t
    response = templates.TemplateResponse("player.html", {"request": request, "video_id": "movie_1"})

    # ITT a varázslat: Beállítjuk a sütit a böngészőben
    # Ez a süti mostantól minden kéréssel automatikusan utazik a szerver felé
    response.set_cookie(
        key=COOKIE_NAME,
        value=SECRET_TOKEN,
        httponly=True,  # Biztonságosabb, JavaScript nem fér hozzá
        max_age=3600  # 1 óráig érvényes
    )

    return response