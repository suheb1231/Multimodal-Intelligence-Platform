
from sentence_transformers import SentenceTransformer
from PIL import Image


# Image embedding model select karna.
MODEL_NAME = "clip-ViT-B-32"


# CLIP model load karna.
model = SentenceTransformer(MODEL_NAME)


def generate_image_embeddings(image_paths):

    # Images load karne ke liye empty list.
    images = []

    # Har image ka path process karna.
    for image_path in image_paths:

        # Image open karke RGB format mein convert karna.
        image = Image.open(image_path).convert("RGB")

        # Loaded image ko list mein add karna.
        images.append(image)

    # Images ko numerical vectors mein convert karna.
    embeddings = model.encode(
        images,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # Generated image embeddings return karna.
    return embeddings
