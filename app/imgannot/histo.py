import pandas as pd
from flask import current_app
from app.src import deepzoom
from glob import glob


def create_deepzoom_file(image_path):
    """Convert an image to a deep zoom image format. Create .dzi file and a folder with the name of the image"""
    # Specify your source image
    SOURCE = image_path
    # Create Deep Zoom Image creator with weird parameters
    creator = deepzoom.ImageCreator(
        tile_size=256,
        tile_overlap=2,
        tile_format="png",
        image_quality=1,
    )
    # Create Deep Zoom image pyramid from source
    creator.create(SOURCE, "" + image_path + ".dzi")


def write_file(data, filename):
    """Convert binary data to proper format and write it on Hard Disk form database"""
    with open(filename, 'wb') as file:
        file.write(data)