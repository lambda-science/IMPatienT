import pandas as pd
from flask import current_app
from app.src import deepzoom
from glob import glob


def create_deepzoom_file(source_path, dest_path):
    """Convert an image to a deep zoom image format. Create .dzi file and a folder with the name of the image"""
    # Create Deep Zoom Image creator with parameters
    creator = deepzoom.ImageCreator(
        tile_size=256,
        tile_overlap=2,
        tile_format="png",
        image_quality=1,
    )
    # Create Deep Zoom image pyramid from source
    creator.create(source_path, dest_path + ".dzi")
