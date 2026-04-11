from fastapi import APIRouter, UploadFile, File, Depends, HTTPException,Query
from sqlmodel import Session, select,func
from typing import Optional
import pandas as pd
from io import BytesIO

from backend.app.db.session import get_session
from backend.app.models.polling_station import PollingStation
from backend.app.models.officer import Officer
from backend.app.core.dependencies import get_current_admin

router = APIRouter()

@router.post("/upload-excel")
async def upload_excel(
    file: UploadFile = File(...),
    admin = Depends(get_current_admin),
    session: Session = Depends(get_session),
):
    # 1️⃣ Check file type
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are allowed")

    # 2️⃣ Read Excel
    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading Excel: {str(e)}")

    rows_inserted = 0
    duplicates_skipped = 0
    records_to_insert = []

    # Determine dataset_id automatically
    max_dataset = session.exec(select(func.max(PollingStation.dataset_id))).first()
    dataset_id = 1 if max_dataset is None else max_dataset + 1

    # Fetch existing records to skip duplicates
    existing = session.exec(select(PollingStation.username, PollingStation.location_name)).all()
    existing_set = set(existing)

    # ✅ Pre-load all officers once before the loop
    existing_officers = session.exec(select(Officer)).all()
    officer_map = {o.username: o for o in existing_officers}

    for _, row in df.iterrows():
        # parse username
        username = row.get("username")
        if pd.isna(username):
            continue
        username = str(username)
        # parse location_name
        location_name = row.get("location_name")
        if pd.isna(location_name):
            location_name = None
        else:
            location_name = str(location_name)
        try:
            s_no = int(row["s_no"])
        except (ValueError, TypeError):
            s_no = None

        # 1️⃣ Update or insert Officer
        officer = officer_map.get(username)  # ✅ dict lookup instead of DB query

        if officer:
            officer.name = safe_update(row.get("name"), officer.name)
            officer.rank = safe_update(row.get("rank"), officer.rank)
            officer.police_station = safe_update(row.get("police_station"), officer.police_station)
            officer.sub_division = safe_update(row.get("sub_division"), officer.sub_division)
            officer.mobile_station = safe_update(row.get("mobile_station"), officer.mobile_station)
            officer.cugphno = safe_update(row.get("cugphno"), officer.cugphno)
        else:
            officer = Officer(
                username=username,
                name=safe_val(row.get("name")),
                rank=safe_val(row.get("rank")),
                police_station=safe_val(row.get("police_station")),
                sub_division=safe_val(row.get("sub_division")),
                mobile_station=safe_val(row.get("mobile_station")),
                cugphno=safe_val(row.get("cugphno"))
            )
            session.add(officer)
            officer_map[username] = officer  # track new officers within the same file

        # Skip if both username and location_name are missing
        if not username or not location_name:
            continue

        # 2️⃣ Skip duplicates for PollingStation
        key = (username, location_name)
        if key in existing_set:
            duplicates_skipped += 1
            continue

        # 3️⃣ Create PollingStation record
        record = PollingStation(
            dataset_id=dataset_id,
            s_no=s_no,
            username=username,
            location_name=location_name
        )
        records_to_insert.append(record)
        rows_inserted += 1
        existing_set.add(key)

    # 4️⃣ Bulk insert
    if records_to_insert:
        for record in records_to_insert:
            session.add(record)
    session.commit()

    return {
        "message": "Dataset uploaded successfully",
        "rows_inserted": rows_inserted,
        "duplicates_skipped": duplicates_skipped
    }


@router.get("/excel")
def get_dataset(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    admin = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    # 1️⃣ Base query
    query = select(PollingStation)

    # 2️⃣ Optional search filter (username or location_name)
    if search:
        search_str = f"%{search}%"
        query = query.where(
            (PollingStation.username.ilike(search_str)) |
            (PollingStation.location_name.ilike(search_str))
        )

    # 3️⃣ Count total matching rows
    total = session.exec(select(func.count()).select_from(query.subquery())).one()

    # 4️⃣ Pagination
    offset = (page - 1) * page_size
    try:
        results = session.exec(query.offset(offset).limit(page_size)).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch records")

    # 5️⃣ Format rows
    rows = [
        {
            "username": r.username,
            "location_name": r.location_name,
            "s_no": r.s_no,
            "dataset_id": r.dataset_id
        } for r in results
    ]

    return {
        "columns": ["username", "location_name", "s_no", "dataset_id"],
        "rows": rows,
        "total": total
    }

@router.get("/officers")
def get_officers(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    admin = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    # 1️⃣ Base query
    query = select(Officer)

    # 2️⃣ Optional search filter (username, name, or rank)
    if search:
        search_str = f"%{search}%"
        query = query.where(
            (Officer.username.ilike(search_str)) |
            (Officer.name.ilike(search_str)) |
            (Officer.rank.ilike(search_str))
        )

    # 3️⃣ Total matching rows
    total = session.exec(select(func.count()).select_from(query.subquery())).one()

    # 4️⃣ Pagination
    offset = (page - 1) * page_size
    try:
        results = session.exec(query.offset(offset).limit(page_size)).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch records")

    # 5️⃣ Format rows
    rows = [
        {
            "username": o.username,
            "name": o.name,
            "rank": o.rank,
            "police_station": o.police_station,
            "sub_division": o.sub_division,
            "mobile_station": o.mobile_station,
            "cugphno": o.cugphno,
            "created_at": o.created_at
        } for o in results
    ]

    return {
        "columns": ["username", "name", "rank", "police_station", "sub_division", "mobile_station", "cugphno", "created_at"],
        "rows": rows,
        "total": total
    }

def safe_update(new, old):
    import pandas as pd
    return old if pd.isna(new) else new

def safe_val(val):
    return None if pd.isna(val) else val