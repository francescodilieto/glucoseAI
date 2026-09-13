"""
Downloads the FULL Dexcom CGM stream for every participant in the BIG IDEAs
Lab dataset (all ~8-10 days each, not the 3-day demo subset) into
training-data/, for offline model training. This directory is gitignored:
only the trained model artifact gets committed, not the raw training data.

Source: https://physionet.org/content/big-ideas-glycemic-wearable/1.1.2/
See docs/DATASET.md for license/attribution.
"""

from pathlib import Path

from extract_demo_data import BASE_URL, extract_egv_rows, fetch_dexcom_csv, write_demo_csv

ALL_PARTICIPANT_IDS = [f"{i:03d}" for i in range(1, 17)]
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "training-data"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for participant_id in ALL_PARTICIPANT_IDS:
        try:
            raw_csv = fetch_dexcom_csv(participant_id)
        except Exception as e:  # noqa: BLE001 - best-effort bulk download
            print(f"patient {participant_id}: FAILED ({e})")
            continue

        egv_rows = extract_egv_rows(raw_csv)
        output_path = OUTPUT_DIR / f"patient_{participant_id}.csv"
        write_full_csv(output_path, egv_rows)
        print(f"patient {participant_id}: {len(egv_rows)} readings -> {output_path}")


def write_full_csv(output_path: Path, rows: list[dict]) -> None:
    import csv

    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "glucose_mg_dl"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
