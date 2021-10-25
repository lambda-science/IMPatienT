import json


class Ontology:
    """A class to handle transformation of ontology"""

    def __init__(self, json_content: list):
        self.jstree_as_list = json_content
        self.jstree_as_dict = {
            i["id"]: {
                "id": i["id"],
                "text": i["text"],
                "icon": i["icon"],
                "data": i["data"],
                "parent": i["parent"],
            }
            for i in self.jstree_as_list
        }

    def update_ontology(self, dest_onto: object) -> dict:
        """Function to update the current ontology tree
        used for anotation with latest modifications of the destination
        (template) of the ontology tree (delete, update, create new, check parents)"""
        updated_jstree_as_list = []

        for i in self.jstree_as_list:
            if i["id"] not in dest_onto.jstree_as_dict.keys():
                # If destination is missing a node: mark the node as outdated
                i["data"]["outdated"] = True
                if "OUTDATED" not in i["text"]:
                    i["text"] = "OUTDATED : " + i["text"]
                updated_jstree_as_list.append(i)
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
                    i["data"]["phenotype"] = dest_onto.jstree_as_dict[i["id"]][
                        "data"
                    ].get("phenotype", "")
                    i["data"]["phenotype_datamined"] = dest_onto.jstree_as_dict[
                        i["id"]
                    ]["data"].get("phenotype_datamined", "")
                    i["data"]["gene_datamined"] = dest_onto.jstree_as_dict[i["id"]][
                        "data"
                    ].get("gene_datamined", "")
                    i["data"]["french_translation"] = dest_onto.jstree_as_dict[i["id"]][
                        "data"
                    ].get("french_translation", "")
                    i["data"]["correlates_with"] = dest_onto.jstree_as_dict[i["id"]][
                        "data"
                    ].get("correlates_with", "")
                    i["data"]["synonymes"] = dest_onto.jstree_as_dict[i["id"]][
                        "data"
                    ].get("synonymes", "")
                updated_jstree_as_list.append(i)
        # If destination has new entry: add them
        for i in dest_onto.jstree_as_dict.keys():
            if i not in self.jstree_as_dict.keys():
                updated_jstree_as_list.append(dest_onto.jstree_as_dict[i])
        self.jstree_as_dict = {
            j["id"]: {
                "id": j["id"],
                "text": j["text"],
                "icon": j["icon"],
                "data": j["data"],
                "parent": j["parent"],
            }
            for j in updated_jstree_as_list
        }

        # If destination has different parent ID: change it.
        for i in dest_onto.jstree_as_dict.keys():
            if (
                dest_onto.jstree_as_dict[i]["parent"]
                != self.jstree_as_dict[i]["parent"]
            ):
                self.jstree_as_dict[i]["parent"] = dest_onto.jstree_as_dict[i]["parent"]

        self.jstree_as_list = list(self.jstree_as_dict.values())
        self.clean_tree()
        return self.jstree_as_list

    def dump_updated_to_file(self, file_path: str):
        with open(file_path, "w") as fp:
            json.dump(self.jstree_as_dict, fp, indent=4)

    def clean_tree(self) -> list:
        clean_tree_list = []
        for i in self.jstree_as_dict:
            clean_tree_list.append(self.jstree_as_dict[i])
        self.jstree_as_list = clean_tree_list
        return self.jstree_as_list
