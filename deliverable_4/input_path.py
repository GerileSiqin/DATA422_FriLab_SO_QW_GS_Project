"""Ask for a local CSV file before running a cleaning script."""

from pathlib import Path


def ask_csv_path(default_file, dataset_name):
    """Accept a CSV path or a folder containing the expected filename."""
    default_file = Path(default_file)
    print(f"\nSelect the {dataset_name} input CSV.")
    print(f"Default: {default_file}")
    print("Paste a CSV file path or its folder path.")
    print("Press Enter to use the default, or type q to cancel.")

    while True:
        try:
            entered = input("Input path: ").strip()
        except (EOFError, KeyboardInterrupt):
            raise SystemExit("\nInput cancelled. No data was processed.") from None

        if entered.lower() == "q":
            raise SystemExit("Input cancelled. No data was processed.")

        # Accept paths copied with surrounding single or double quotes.
        if len(entered) >= 2 and entered[0] == entered[-1] and entered[0] in "\"'":
            entered = entered[1:-1]

        path = Path(entered).expanduser() if entered else default_file
        if path.is_dir():
            path = path / default_file.name

        if not path.is_file():
            print(f"File not found: {path}")
            print("Try again. If the CSV has a different name, enter its full file path.")
            continue
        if path.suffix.lower() != ".csv":
            print("Please select a CSV file (.csv).")
            continue
        try:
            with path.open("rb"):
                pass
        except OSError as error:
            print(f"Cannot read this file: {error}")
            continue
        return path.resolve()
