import asyncio
import json
from pathlib import Path

from decision_platform.config import Settings
from decision_platform.contracts import Opportunity
from decision_platform.factory import build_engine


async def _run() -> None:
    payload = json.loads(Path("data/synthetic_opportunity.json").read_text(encoding="utf-8"))
    outcome = await build_engine(Settings(scoring_url="http://localhost:8081")).run(
        Opportunity.model_validate(payload)
    )
    print(outcome.model_dump_json(indent=2))


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
