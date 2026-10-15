"""Download all in-scope source files without requiring a Koordinates key."""
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline.sources import prepare_inputs

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    config = json.loads((ROOT / "config/project.json").read_text())
    manifest = prepare_inputs(ROOT, config, True)
    print("Downloaded months:", [x["snapshot_month"] for x in manifest["airbnb"]])
    print("Missing months:", manifest["missing_airbnb_months"])
