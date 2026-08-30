from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from financial_engineering.application.datasets.datasets_controller import (
    router as datasets_router,
)
from financial_engineering.application.use_cases.get_data.get_data_controller import (
    router as data_router,
)
from financial_engineering.application.use_cases.get_history.get_history_controller import (
    router as history_router,
)


app = FastAPI(
    title='Financial Engineering Data API',
    description='HTTP access to the LSEG data extraction workflow.',
    version='0.1.0',
)
app.include_router(data_router)
app.include_router(history_router)
app.include_router(datasets_router)

FRONTEND_DIR = Path(__file__).resolve().parents[2] / 'frontend'
load_dotenv(Path(__file__).resolve().parents[2] / '.env')


@app.get('/', response_model=None)
def root() -> Any:
    if (FRONTEND_DIR / 'index.html').is_file():
        return FileResponse(FRONTEND_DIR / 'index.html')
    return {
        'name': 'Financial Engineering Data API',
        'docs': '/docs',
        'health': '/health',
        'data': '/data',
        'history': '/history',
    }


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}


def main() -> None:
    import uvicorn

    uvicorn.run(
        'financial_engineering.app:app',
        host=os.getenv('API_HOST', '127.0.0.1'),
        port=int(os.getenv('API_PORT', '8000')),
    )


if FRONTEND_DIR.is_dir():
    app.mount('/', StaticFiles(directory=FRONTEND_DIR, html=True), name='frontend')


if __name__ == '__main__':
    main()
