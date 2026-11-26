
# Path aur file information handle karne ke liye Path import karna.
from pathlib import Path

# Existing asset registry se registered assets retrieve karna.
from ingestion.asset_registry import get_all_assets


# Project ka main folder identify karna.
BASE_DIR = Path(__file__).resolve().parent.parent

# Uploaded assets ka folder define karna.
UPLOAD_DIR = BASE_DIR / "data" / "uploads"


# Supported modalities define karna.
SUPPORTED_MODALITIES = {
    "pdf",
    "video",
    "audio",
    "image",
    "text",
    "quiz",
    "discussion"
}


# Asset ki profile generate karne wala function.
def profile_asset(asset_id):

    # Registry se saare registered assets retrieve karna.
    assets = get_all_assets()

    # Requested asset ko search karna.
    for asset in assets:

        # Database record se asset ki details nikalna.
        (
            registered_id,
            filename,
            modality,
            owner,
            permission_scope,
            processing_status,
            created_at
        ) = asset

        # Requested asset ID match karna.
        if registered_id == asset_id:

            # Filename se safe file name identify karna.
            safe_filename = Path(filename).name

            # Uploaded file ka actual path create karna.
            file_path = UPLOAD_DIR / safe_filename

            # Check karna ki uploaded file exist karti hai.
            file_exists = file_path.is_file()

            # File ka extension identify karna.
            file_extension = file_path.suffix.lower()

            # File ka size available hone par calculate karna.
            file_size = file_path.stat().st_size if file_exists else None

            # Modality supported hai ya nahi check karna.
            modality_supported = modality.lower() in SUPPORTED_MODALITIES

            # Asset ki complete profile prepare karna.
            profile = {
                "asset_id": registered_id,
                "filename": filename,
                "modality": modality,
                "asset_type": modality,
                "file_extension": file_extension,
                "file_exists": file_exists,
                "file_size_bytes": file_size,
                "modality_supported": modality_supported,
                "owner": owner,
                "permission_scope": permission_scope,
                "processing_status": processing_status,
                "created_at": created_at,
                "profile_status": (
                    "profiled"
                    if file_exists and modality_supported
                    else "needs_attention"
                )
            }

            # Generated asset profile return karna.
            return profile

    # Asset registry mein nahi mila toh None return karna.
    return None
