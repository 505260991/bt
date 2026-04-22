from pathlib import Path
from urllib.parse import unquote

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, Response
import httpx

app = FastAPI()

BASE = "https://web5.mukaku.com/prod/api/v1/"
APP_ID = "83768d9ad4"
IDENTITY = "23734adac0301bccdcb107c4aa21f96c"
ROOT_DIR = Path(__file__).resolve().parent
INDEX_FILE = ROOT_DIR / "index.html"


def normalize_media_url(url: str | None) -> str:
    if not url:
        return ""

    url = unquote(str(url)).strip()
    if url.startswith("//"):
        return f"https:{url}"
    if url.startswith("/"):
        return f"https://web5.mukaku.com{url}"
    return url


def get_params(extra: dict):
    return {
        "app_id": APP_ID,
        "identity": IDENTITY,
        **extra,
    }


@app.get("/")
async def home():
    return FileResponse(INDEX_FILE)


# 🔍 搜索接口
@app.get("/search")
async def search(q: str, page: int = 1):
    async with httpx.AsyncClient() as client:
        r = await client.get(
            BASE + "getVideoList",
            params=get_params({"sb": q, "page": page, "limit": 24}),
        )
        data = r.json()

    result = []
    for v in data.get("data", {}).get("data", []):
        result.append(
            {
                "id": v.get("doub_id"),
                "title": v.get("title"),
                "cover": normalize_media_url(v.get("cover") or v.get("poster")),
                "rate": v.get("rate"),
            }
        )

    return result


# 📄 详情 + 磁力
@app.get("/detail")
async def detail(id: int):
    async with httpx.AsyncClient() as client:
        r = await client.get(BASE + "getVideoDetail", params=get_params({"id": id}))
        data = r.json()

    seeds = data.get("data", {}).get("all_seeds", [])

    result = []
    for s in seeds:
        if str(s.get("zlink", "")).startswith("magnet:"):
            result.append(
                {
                    "name": s.get("zname"),
                    "size": s.get("zsize"),
                    "quality": s.get("zqxd"),
                    "magnet": s.get("zlink"),
                }
            )

    return result


# 🖼 图片代理（防盗链）
@app.get("/img")
async def img(url: str):
    url = normalize_media_url(url)
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="invalid image url")

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://web5.mukaku.com/",
    }

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            r = await client.get(url, headers=headers)
            if r.status_code >= 400:
                return RedirectResponse(url=url, status_code=307)

            media_type = r.headers.get("content-type", "image/jpeg").split(";")[0]
            return Response(content=r.content, media_type=media_type)
    except httpx.HTTPError:
        return RedirectResponse(url=url, status_code=307)
