import pandas as pd
from tkinter import Tk, filedialog

from app.db.session import engine
from sqlmodel import Session
from app.models.report import Report

# Conditions for the Excel file:
# - Should have the following columns
# name
# rank
# contact_number
# polling_stations
# polling_locations
# ballot_boxes

def pick_file():
    Tk().withdraw()  # hide root window
    file_path = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    return file_path


def main():
    file_path = pick_file()

    if not file_path:
        print("No file selected.")
        return

    print(f"Reading file: {file_path}")

    try:
        df = pd.read_excel(file_path)

        # Normalize column names
        df.columns = df.columns.str.strip().str.lower()

        if "username" not in df.columns:
            print("❌ 'username' column is required")
            return

        reports = []
        errors = []

        for idx, row in df.iterrows():
            try:
                # -------- VALIDATION --------
                if pd.isna(row.get("username")):
                    errors.append(f"Row {idx+1}: username missing")
                    continue

                # -------- CLEAN DATA --------
                report = Report(
                    username=str(row.get("username")),

                    name=None if pd.isna(row.get("name")) else str(row.get("name")),
                    rank=None if pd.isna(row.get("rank")) else str(row.get("rank")),
                    contact_number=None if pd.isna(row.get("contact_number")) else str(row.get("contact_number")),

                    polling_stations=int(row.get("polling_stations") or 0),
                    polling_locations=int(row.get("polling_locations") or 0),
                    ballot_boxes=int(row.get("ballot_boxes") or 0),
                )

                reports.append(report)

            except Exception as e:
                errors.append(f"Row {idx+1}: {str(e)}")

        # -------- INSERT INTO DB --------
        with Session(engine) as session:
            session.add_all(reports)
            session.commit()

        print("\n✅ Upload Complete")
        print(f"Inserted: {len(reports)} rows")

        if errors:
            print("\n⚠️ Errors:")
            for err in errors:
                print(err)

    except Exception as e:
        print(f"❌ Failed: {str(e)}")


if __name__ == "__main__":
    main()