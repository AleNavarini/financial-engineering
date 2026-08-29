from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from financial_engineering.infrastructure.lseg_client import LsegClient


class GetHistoryUseCase:
    def __init__(self, client: LsegClient | None = None) -> None:
        self.client = client or LsegClient()

    def execute(
        self,
        *,
        instruments: list[str] | None,
        ticker: str | None,
        fields: list[str] | None,
        start: date,
        end: date,
        interval: str,
        output: Path | None = None,
    ) -> dict[str, Any]:
        return self.client.get_history(
            instruments=instruments,
            ticker=ticker,
            fields=fields,
            start=start,
            end=end,
            interval=interval,
            output=output,
        )
