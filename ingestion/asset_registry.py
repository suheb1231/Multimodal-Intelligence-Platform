
import sqlite3
from pathlib import Path
from uuid import uuid4
from datetime import datetime


# Database file ka location define kar rahe hain.
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "asset_registry.db"


# SQLite database aur assets table create karne ke liye.
def create_database():

    # Database folder exist nahi karta toh create karenge.
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Database se connection establish kar rahe hain.
    connection = sqlite3.connect(DATABASE_PATH)

    # SQL queries execute karne ke liye cursor bana rahe hain.
    cursor = connection.cursor()

    # Assets table create kar rahe hain agar pehle se exist nahi karti.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (

            asset_id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            modality TEXT NOT NULL,
            owner TEXT NOT NULL,
            permission_scope TEXT NOT NULL,
            processing_status TEXT NOT NULL,
            created_at TEXT NOT NULL

        )
    """)

    # Database changes save kar rahe hain.
    connection.commit()

    # Database connection close kar rahe hain.
    connection.close()


# New asset ko database mein register karne ke liye.
def register_asset(filename, modality, owner, permission_scope):

    # Har asset ke liye unique ID generate kar rahe hain.
    asset_id = str(uuid4())

    # Database connection create kar rahe hain.
    connection = sqlite3.connect(DATABASE_PATH)

    # SQL queries execute karne ke liye cursor bana rahe hain.
    cursor = connection.cursor()

    # Asset ki details database mein insert kar rahe hain.
    cursor.execute("""
        INSERT INTO assets (
            asset_id,
            filename,
            modality,
            owner,
            permission_scope,
            processing_status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        asset_id,
        filename,
        modality,
        owner,
        permission_scope,
        "uploaded",
        datetime.now().isoformat()
    ))

    # Registered asset ki details save kar rahe hain.
    connection.commit()

    # Database connection close kar rahe hain.
    connection.close()

    # Generated unique asset ID return kar rahe hain.
    return asset_id


# Database mein registered saare assets retrieve karne ke liye.
def get_all_assets():

    # Database connection create kar rahe hain.
    connection = sqlite3.connect(DATABASE_PATH)

    # SQL queries execute karne ke liye cursor bana rahe hain.
    cursor = connection.cursor()

    # Saare assets latest registration ke order mein retrieve kar rahe hain.
    cursor.execute(
        "SELECT * FROM assets ORDER BY created_at DESC"
    )

    # Database se saare records fetch kar rahe hain.
    assets = cursor.fetchall()

    # Database connection close kar rahe hain.
    connection.close()

    # Retrieved assets return kar rahe hain.
    return assets


# Check karne ke liye ki user ko asset access karne ki permission hai ya nahi.
def check_asset_permission(asset_id, user):

    # Database connection create kar rahe hain.
    connection = sqlite3.connect(DATABASE_PATH)

    # SQL queries execute karne ke liye cursor bana rahe hain.
    cursor = connection.cursor()

    # Given asset ki owner aur permission details retrieve kar rahe hain.
    cursor.execute("""
        SELECT owner, permission_scope
        FROM assets
        WHERE asset_id = ?
    """, (asset_id,))

    # Matching asset ka record fetch kar rahe hain.
    result = cursor.fetchone()

    # Database connection close kar rahe hain.
    connection.close()

    # Asset database mein nahi mila toh access deny karenge.
    if result is None:
        return False

    # Database se owner aur permission scope nikal rahe hain.
    owner, permission_scope = result

    # Owner ya public asset ko access allow kar rahe hain.
    if owner == user or permission_scope == "public":
        return True

    # Baaki users ke liye access deny kar rahe hain.
    return False


# Asset ka processing status update karne ke liye.
def update_asset_status(asset_id, new_status):

    # Database connection create kar rahe hain.
    connection = sqlite3.connect(DATABASE_PATH)

    # SQL queries execute karne ke liye cursor bana rahe hain.
    cursor = connection.cursor()

    # Given asset ka processing status update kar rahe hain.
    cursor.execute("""
        UPDATE assets
        SET processing_status = ?
        WHERE asset_id = ?
    """, (new_status, asset_id))

    # Updated status database mein save kar rahe hain.
    connection.commit()

    # Check kar rahe hain ki koi record update hua ya nahi.
    updated_rows = cursor.rowcount

    # Database connection close kar rahe hain.
    connection.close()

    # Update successful hone par True return kar rahe hain.
    return updated_rows > 0


# Database se asset record aur uploaded file delete karne ke liye.
def delete_asset(asset_id):

    # Database connection create kar rahe hain.
    connection = sqlite3.connect(DATABASE_PATH)

    # SQL queries execute karne ke liye cursor bana rahe hain.
    cursor = connection.cursor()

    # Asset ka filename retrieve kar rahe hain.
    cursor.execute(
        "SELECT filename FROM assets WHERE asset_id = ?",
        (asset_id,)
    )

    # Matching asset ka record fetch kar rahe hain.
    result = cursor.fetchone()

    # Asset nahi mila toh deletion stop kar rahe hain.
    if result is None:
        connection.close()
        return False

    # Database record se filename nikal rahe hain.
    filename = result[0]

    # Database se asset ka record delete kar rahe hain.
    cursor.execute(
        "DELETE FROM assets WHERE asset_id = ?",
        (asset_id,)
    )

    # Database changes save kar rahe hain.
    connection.commit()

    # Database connection close kar rahe hain.
    connection.close()

    # Uploaded file ka actual path define kar rahe hain.
    file_path = BASE_DIR / "data" / "uploads" / filename

    # File exist karti hai toh physical file delete kar rahe hain.
    if file_path.exists():
        file_path.unlink()

    # Successful deletion par True return kar rahe hain.
    return True


# Module import hone par database automatically create kar rahe hain.
create_database()
