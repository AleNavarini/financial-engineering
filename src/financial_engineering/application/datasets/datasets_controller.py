from __future__ import annotations

import logging
import time
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from financial_engineering.infrastructure.csv_dataset_store import CsvDatasetStore


logger = logging.getLogger(__name__)
router = APIRouter(prefix='/datasets', tags=['datasets'])
dataset_store = CsvDatasetStore()


@router.get('')
def list_datasets() -> dict[str, Any]:
    started = time.perf_counter()
    datasets = dataset_store.list_datasets()
    logger.info('Listed CSV datasets count=%s duration_ms=%.1f', len(datasets), _duration_ms(started))
    return {'datasets': datasets, 'count': len(datasets)}


@router.get('/{dataset_name}/download')
def download_dataset(dataset_name: str) -> FileResponse:
    try:
        path = dataset_store.get_download_path(dataset_name)
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=404, detail='CSV dataset not found') from error
    logger.info('Downloaded CSV dataset name=%s size_bytes=%s', path.name, path.stat().st_size)
    return FileResponse(path, media_type='text/csv', filename=path.name)


@router.get('/{dataset_name}')
def get_dataset(dataset_name: str) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        dataset = dataset_store.get_dataset(dataset_name)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail='CSV dataset not found') from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    logger.info(
        'Read CSV dataset name=%s rows=%s duration_ms=%.1f',
        dataset['name'],
        dataset['row_count'],
        _duration_ms(started),
    )
    return dataset


def _duration_ms(started: float) -> float:
    return (time.perf_counter() - started) * 1000
