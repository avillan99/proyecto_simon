from datetime import datetime
import json
import pandas as pd
from pathlib import Path

def debug_dump(
    data,
    name: str,
    as_csv: bool = False,
    folder: str = "debug"
):
    Path(folder).mkdir(exist_ok=True)
    # ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = Path(folder) / f"{name}.json"
    json_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    if as_csv and isinstance(data, list):
        try:
            pd.DataFrame(data).to_csv(
                json_path.with_suffix(".csv"),
                index=False
            )
        except Exception:
            pass
