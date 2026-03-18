"""
Data acquisition module for March Madness prediction.

Downloads and organizes data from:
1. Kaggle March Machine Learning Mania competition (foundation)
2. Additional sources as needed (Bart Torvik, KenPom, etc.)
"""

import os
import subprocess
import zipfile
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
KAGGLE_DIR = RAW_DIR / "kaggle"


def download_kaggle_data():
    """Download the March Machine Learning Mania 2025 competition data from Kaggle."""
    KAGGLE_DIR.mkdir(parents=True, exist_ok=True)

    # The competition slug — use the most recent available
    competition = "march-machine-learning-mania-2025"

    print(f"Downloading {competition} data...")
    subprocess.run(
        ["kaggle", "competitions", "download", "-c", competition, "-p", str(KAGGLE_DIR)],
        check=True,
    )

    # Extract any zip files
    for zip_path in KAGGLE_DIR.glob("*.zip"):
        print(f"Extracting {zip_path.name}...")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(KAGGLE_DIR)
        zip_path.unlink()  # Remove zip after extraction

    # List what we got
    csv_files = sorted(KAGGLE_DIR.glob("*.csv"))
    print(f"\nDownloaded {len(csv_files)} CSV files:")
    for f in csv_files:
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {f.name} ({size_mb:.1f} MB)")

    return csv_files


def verify_kaggle_data():
    """Check that expected Kaggle files are present."""
    expected_prefixes = [
        "MTeams",
        "MSeasons",
        "MRegularSeasonCompactResults",
        "MRegularSeasonDetailedResults",
        "MNCAATourneyCompactResults",
        "MNCAATourneyDetailedResults",
        "MNCAATourneySeeds",
        "MConferenceTourneyGames",
        "MMasseyOrdinals",
        "MGameCities",
        "Cities",
    ]

    missing = []
    for prefix in expected_prefixes:
        matches = list(KAGGLE_DIR.glob(f"{prefix}*.csv"))
        if not matches:
            missing.append(prefix)

    if missing:
        print(f"WARNING: Missing expected files with prefixes: {missing}")
    else:
        print("All expected Kaggle data files present.")

    return len(missing) == 0


if __name__ == "__main__":
    download_kaggle_data()
    verify_kaggle_data()
