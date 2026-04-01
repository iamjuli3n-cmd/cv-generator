from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from classCV import CV
from cv_test import cv_test

app = FastAPI(title="CV Generator")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def accueil(request: Request):
    return templates.TemplateResponse(
        request=request, name="cv.html", context={"cv": cv_test}
    )


@app.get("/cv/json", response_model=CV)
def get_cv_json():
    return cv_test


@app.get("/cv2", response_class=HTMLResponse)
def accueil_v2(request: Request):
    return templates.TemplateResponse(
        request=request, name="cv2.html", context={"cv": cv_test}
    )
