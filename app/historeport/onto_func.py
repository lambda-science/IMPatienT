import json


class Ontology:
    """A class to handle transformation of ontology"""

    def __init__(self, json_content: list):
        self.raw_jstree = json_content
        self.jstree_as_dict = {
            i["id"]: {
                "id": i["id"],
                "text": i["text"],
                "icon": i["icon"],
                "data": i["data"],
                "parent": i["parent"],
            }
            for i in self.raw_jstree
        }
        self.updated_jstree_dict = {}

    def update_ontology(self, dest_onto: object) -> dict:
        """Function to update the current ontology tree
        used for anotation with latest modifications of the destination
        (template) of the ontology tree (delete, update, create new)"""
        updated_jstree_as_dict = []

        for i in self.raw_jstree:
            if i["id"] not in dest_onto.jstree_as_dict.keys():
                # If destination is missing a node: mark the node as outdated
                i["data"]["outdated"] = True
                if "OUTDATED" not in i["text"]:
                    i["text"] = "OUTDATED : " + i["text"]
                updated_jstree_as_dict.append(i)
            elif i["id"] in dest_onto.jstree_as_dict.keys():
                if (
                    i["text"] != dest_onto.jstree_as_dict[i["id"]]["text"]
                    or i["data"] != dest_onto.jstree_as_dict[i["id"]]["data"]
                ):
                    # If destination has modified data or name: update
                    i["data"].setdefault("old_name", []).append(i["text"])
                    i["text"] = dest_onto.jstree_as_dict[i["id"]]["text"]
                    i["data"]["description"] = dest_onto.jstree_as_dict[i["id"]][
                        "data"
                    ].get("description", "")
                    i["data"]["genes"] = dest_onto.jstree_as_dict[i["id"]]["data"].get(
                        "genes", ""
                    )
                    i["data"]["synonymes"] = dest_onto.jstree_as_dict[i["id"]][
                        "data"
                    ].get("synonymes", "")
                updated_jstree_as_dict.append(i)
        # If destination has new entry: add them
        for i in dest_onto.jstree_as_dict.keys():
            if i not in self.jstree_as_dict.keys():
                updated_jstree_as_dict.append(dest_onto.jstree_as_dict[i])
        self.updated_jstree_dict = updated_jstree_as_dict
        return updated_jstree_as_dict

    def dump_updated_to_file(self, file_path: str):
        with open(file_path, "w") as fp:
            json.dump(self.updated_jstree_dict, fp, indent=4)
