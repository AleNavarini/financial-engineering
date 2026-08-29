from __future__ import annotations

from pathlib import Path
from typing import Any

from financial_engineering.infrastructure.lseg_client import LsegClient


class GetDataUseCase:
    def __init__(self, client: LsegClient | None = None) -> None:
        self.client = client or LsegClient()

    def execute(
        self,
        *,
        instruments: list[str] | None,
        ticker: str | None,
        fields: list[str] | None,
        output: Path | None = None,
    ) -> dict[str, Any]:
        return self.client.get_data(
            instruments=instruments,
            ticker=ticker,
            fields=fields,
            output=output,
        )
