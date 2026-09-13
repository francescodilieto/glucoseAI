"""
Downloads a small CGM demo subset from the public BIG IDEAs Lab Glycemic
Variability and Wearable Device Data (PhysioNet, Open Data Commons
Attribution License v1.0) and writes clean per-patient CSVs to data/demo/.

Only the Dexcom CGM stream is used (glucose value every ~5 minutes).
Wearable signals (ACC/BVP/EDA/HR/IBI/TEMP) and food logs are ignored.

Source: https://physionet.org/content/big-ideas-glycemic-wearable/1.1.2/
Citation: Cho, Kim, Bent & Dunn (2023); Bent et al., Nature Digital
Medicine (2021). See docs/DATASET.md for full attribution.
"""

import csv
import io
import urllib.request
from pathlib import Path

BASE_URL = "https://physionet.org/files/big-ideas-glycemic-wearable/1.1.2"
PARTICIPANT_IDS = ["001", "002", "003"]
DAYS_TO_KEEP = 3
POINTS_PER_DAY = 288  # 24h * 60min / 5min sampling
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "demo"


def fetch_dexcom_csv(participant_id: str) -> str:
    url = f"{BASE_URL}/{participant_id}/Dexcom_{participant_id}.csv"
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read().decode("utf-8")


def extract_egv_rows(raw_csv: str) -> list[dict]:
    """Keep only 'EGV' (Estimated Glucose Value) rows: real CGM readings.

    The raw file mixes patient metadata and alert-threshold rows in with
    the actual glucose readings, all under the same columns.
    """
    reader = csv.DictReader(io.StringIO(raw_csv))
    rows = []
    for row in reader:
        if row.get("Event Type") != "EGV":
            continue
        timestamp = row.get("Timestamp (YYYY-MM-DDThh:mm:ss)", "").strip()
        glucose = row.get("Glucose Value (mg/dL)", "").strip()
        if not timestamp or not glucose:
            continue
        rows.append({"timestamp": timestamp.replace(" ", "T"), "glucose_mg_dl": glucose})
    return rows


def write_demo_csv(participant_id: str, rows: list[dict]) -> Path:
    subset = rows[: DAYS_TO_KEEP * POINTS_PER_DAY]
    output_path = OUTPUT_DIR / f"patient_{participant_id}.csv"
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "glucose_mg_dl"])
        writer.writeheader()
        writer.writerows(subset)
    return output_path


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for participant_id in PARTICIPANT_IDS:
        raw_csv = fetch_dexcom_csv(participant_id)
        egv_rows = extract_egv_rows(raw_csv)
        output_path = write_demo_csv(participant_id, egv_rows)
        print(f"patient {participant_id}: {len(egv_rows)} readings -> {output_path} "
              f"({min(len(egv_rows), DAYS_TO_KEEP * POINTS_PER_DAY)} kept)")


if __name__ == "__main__":
    main()
