import pandas as pd
from flask import current_app
from app.src import deepzoom
from glob import glob


def create_feature_list(config_file):
    """Extract the list of feature and format them from the configuration file path"""
    feature_df = pd.read_csv(config_file, sep='\t', header=None)
    feature_list = [(row[0].strip().replace(" ", "_"), row[0], row[1])
                    for index, row in feature_df.iterrows()]
    return feature_list


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


def create_history_file():
    """List all images with allowed extensions in the upload folder"""
    file_list = [
        (i.split("/")[-1].split("_")[0], i.split("/")[-1])
        for i in glob("uploads/*")
        if i.split(".")[-1] in current_app.config["ALLOWED_EXTENSIONS"]
    ]
    return file_list


def write_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)