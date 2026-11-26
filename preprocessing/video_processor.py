
import cv2
# OpenCV library video ko read aur frames extract karne ke liye hai.

from pathlib import Path
# Path folders aur file locations handle karne ke liye hai.

from uuid import uuid4
# Har extracted frame ko unique ID dene ke liye hai.


def extract_video_frames(video_path, asset_id, interval_seconds=5):
    # Ye function video se fixed interval par frames extract karega.

    video_path = Path(video_path)
    # Video file ke path ko Path format mein convert kar rahe hain.

    if not video_path.exists():
        # Check kar rahe hain ki video file exist karti hai ya nahi.

        raise FileNotFoundError("Video file not found")
        # File nahi mili to error show hoga.

    if video_path.suffix.lower() not in [".mp4", ".mov"]:
        # Check kar rahe hain ki video MP4 ya MOV format mein hai.

        raise ValueError("Only MP4 and MOV videos are supported")
        # Doosra format hua to error show hoga.

    if interval_seconds <= 0:
        # Check kar rahe hain ki frame interval zero ya negative na ho.

        raise ValueError("Interval must be greater than zero")
        # Galat interval hone par error show hoga.

    project_dir = Path(__file__).resolve().parent.parent
    # Project ka main folder locate kar rahe hain.

    output_dir = project_dir / "data" / "processed" / asset_id / "frames"
    # Is video ke frames save karne ke liye folder ka path bana rahe hain.

    output_dir.mkdir(parents=True, exist_ok=True)
    # Folder exist nahi karta to automatically create hoga.

    cap = cv2.VideoCapture(str(video_path))
    # OpenCV ke through video open kar rahe hain.

    if not cap.isOpened():
        # Check kar rahe hain ki video successfully open hui ya nahi.

        raise ValueError("Unable to open video")
        # Video open nahi hui to error show hoga.

    fps = cap.get(cv2.CAP_PROP_FPS)
    # Video ke frames per second (FPS) read kar rahe hain.

    if fps <= 0:
        # Check kar rahe hain ki FPS valid hai ya nahi.

        cap.release()
        # Video resource release kar rahe hain.

        raise ValueError("Invalid video FPS")
        # FPS invalid hua to error show hoga.

    frame_step = max(1, round(fps * interval_seconds))
    # Calculate kar rahe hain ki kitne frames skip karne hain.

    extracted_frames = []
    # Extracted frames ki information is list mein store hogi.

    frame_index = 0
    # Video ka frame counter zero se start hoga.

    try:
        # Video processing ko safely run karne ke liye try block.

        while True:
            # Jab tak video mein frames milte rahenge, loop chalega.

            success, frame = cap.read()
            # Video se next frame read kar rahe hain.

            if not success:
                # Agar frame nahi mila to video khatam ho gayi.

                break
                # Loop stop kar rahe hain.

            if frame_index % frame_step == 0:
                # Check kar rahe hain ki ye frame extract karna hai ya nahi.

                timestamp = frame_index / fps
                # Frame ka timestamp seconds mein calculate kar rahe hain.

                frame_id = str(uuid4())
                # Frame ko unique ID de rahe hain.

                frame_name = f"frame_{frame_index:06d}.jpg"
                # Frame ka filename create kar rahe hain.

                frame_path = output_dir / frame_name
                # Frame save karne ki location bana rahe hain.

                saved = cv2.imwrite(str(frame_path), frame)
                # Extracted image ko JPG file mein save kar rahe hain.

                if not saved:
                    # Check kar rahe hain ki image successfully save hui ya nahi.

                    raise ValueError("Unable to save extracted frame")
                    # Save failure hone par error show hoga.

                extracted_frames.append({
                    # Frame ki details list mein add kar rahe hain.

                    "frame_id": frame_id,
                    # Har frame ki unique identity.

                    "asset_id": asset_id,
                    # Original video ki asset identity.

                    "source_file": video_path.name,
                    # Original video ka filename.

                    "timestamp_seconds": round(timestamp, 2),
                    # Video mein frame kis time par tha.

                    "frame_path": str(frame_path),
                    # Extracted image ki file location.

                    "modality": "video_frame"
                    # Batata hai ki ye image video se extract hui hai.
                })
                # Frame ki saari metadata information complete.

            frame_index += 1
            # Agle frame ke liye counter increase kar rahe hain.

    finally:
        # Processing complete ho ya error aaye, ye block chalega.

        cap.release()
        # Video resource release kar rahe hain.

    return extracted_frames
    # Extracted frames ki complete information return kar rahe hain.
