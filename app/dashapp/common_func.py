import os
import json


def load_onto():
    with open(os.path.join("data/ontology", "ontology.json"), "r") as fp:
        onto_tree = json.load(fp)
    id_img_annot_section = [
        i["id"] for i in onto_tree if i["text"] == "Image Annotations"
    ][0]
    onto_tree_imgannot = []
    for node in onto_tree:
        if node["parent"] == id_img_annot_section:
            onto_tree_imgannot.append(node)
    return onto_tree_imgannot
