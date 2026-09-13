from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from financial_engineering.infrastructure.yahoo_client import YahooClient


class GetYahooHistoryUseCase:
    def __init__(self, client: YahooClient | None = None) -> None:
        self.client = client or YahooClient()

    def execute(
        self,
        *,
        ticker: str,
        fields: list[str] | None,
        start: date,
        end: date,
        interval: str,
        output: Path | None = None,
    ) -> dict[str, Any]:
        return self.client.get_history(
            ticker=ticker,
            fields=fields,
            start=start,
            end=end,
            interval=interval,
            output=output,
        )
