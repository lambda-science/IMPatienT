import json
import random
from pronto import Ontology, Definition
import io
from flask_wtf.file import FileField


class ImpatientVocab:
    def __init__(self) -> None:
        self.used_colors: list[str] = []
        self.impatient_json: list[dict] = []
        self.impatient_onto: Ontology = None
        self.list_of_terms: list[str] = []

    def load_json(self, path: str) -> list[dict]:
        self.impatient_json = json.load(open(path, "r"))
        return self.impatient_json

    def load_ontology(self, path: str) -> Ontology:
        self.impatient_onto = Ontology(path)
        return self.impatient_onto

    def load_json_f(self, file: FileField) -> list[dict]:
        # Read the JSON data from the file object
        json_data = json.loads(file.read())
        self.impatient_json = json_data
        return json_data

    def load_ontology_f(self, file: FileField) -> Ontology:
        # Read the ontology data from the file object
        ontology_data = io.BytesIO(file.read())
        ontology = Ontology(ontology_data)
        self.impatient_onto = ontology
        return ontology

    def json_to_onto(self) -> Ontology:
        self.impatient_onto = Ontology()
        term_mapping = (
            {}
        )  # A dictionary to store term IDs and their corresponding created terms

        # First pass: Create terms without adding superclasses
        for term in self.impatient_json:
            term_id = term["id"].replace("_", ":")
            added_term = self.impatient_onto.create_term(term_id)
            added_term.name = term["text"]
            for syn in term["data"]["synonymes"].split(","):
                if syn.strip() != "":
                    added_term.add_synonym(syn.strip(), scope="EXACT")
            if term["data"]["description"] != "":
                added_term.definition = Definition(term["data"]["description"])

            term_mapping[term_id] = added_term  # Store the term in the mapping

        # Second pass: Add superclasses
        for term in self.impatient_json:
            term_id = term["id"].replace("_", ":")
            added_term = term_mapping[term_id]

            if term["parent"] != "#":
                parent_id = term["parent"].replace("_", ":")
                parent_term = term_mapping.get(parent_id)
                if parent_term:
                    added_term.superclasses().add(parent_term)

            self.list_of_terms.append(added_term)

        return self.impatient_onto

    def onto_to_json(self) -> list[dict]:
        self.impatient_json = []
        index = 0
        for term in self.impatient_onto.terms():
            relationships = []
            for rel in term.superclasses():
                relationships.append(rel.id)
            relationships.pop(0)
            self.impatient_json.append(
                {
                    "id": term.id.replace("_", ":"),
                    "text": term.name if term.name is not None else "",
                    "icon": True,
                    "data": {
                        "description": term.definition
                        if term.definition is not None
                        else "",
                        "synonymes": ",".join(
                            [syn.description for syn in term.synonyms]
                        ),
                        "phenotype_datamined": "",
                        "gene_datamined": "",
                        "alternative_language": term.name
                        if term.name is not None
                        else "",
                        "correlates_with": "",
                        "image_annotation": True if index == 0 else False,
                        "hex_color": self._generate_hex_color(),
                        "hpo_datamined": "",
                    },
                    "parent": relationships[0].replace("_", ":")
                    if relationships != []
                    else "#",
                }
            )
            index += 1
        return self.impatient_json

    def _generate_hex_color(self):
        while True:
            # Generate a random hex color
            color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            # Check if the color has already been used
            if color not in self.used_colors:
                # Add the color to the list of used colors and return it
                self.used_colors.append(color)
                return color

    def dump_onto(self, path: str) -> None:
        with open(path, "wb") as f:
            self.impatient_onto.dump(f, format="obo")

    def dump_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.impatient_json, f, indent=2)


class StandardVocabulary:
    """Class for the standard vocabulary"""

    def __init__(self, json_content: list):
        """Initiliaze the class with the json tree content (from JSTree)

        Args:
            json_content (list): JSON from JSTree
        """
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

    def update_ontology(self, dest_onto: object) -> list:
        """Update the current standard vocabulary tree with the latest modification
        (destination) of the tree (delete, add, update, check parents).

        Args:
            dest_onto (object): Another instance of the class StandardVocabulary

        Returns:
            list: return the updated tree as list of dict (json)
        """
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
                    i["text"] = dest_onto.jstree_as_dict[i["id"]]["text"]
                    i["data"]["description"] = dest_onto.jstree_as_dict[i["id"]][
                        "data"
                    ].get("description", "")
                    i["data"]["hpo_datamined"] = dest_onto.jstree_as_dict[i["id"]][
                        "data"
                    ].get("hpo_datamined", "")
                    i["data"]["phenotype_datamined"] = dest_onto.jstree_as_dict[
                        i["id"]
                    ]["data"].get("phenotype_datamined", "")
                    i["data"]["gene_datamined"] = dest_onto.jstree_as_dict[i["id"]][
                        "data"
                    ].get("gene_datamined", "")
                    i["data"]["alternative_language"] = dest_onto.jstree_as_dict[
                        i["id"]
                    ]["data"].get("alternative_language", "")
                    i["data"]["correlates_with"] = dest_onto.jstree_as_dict[i["id"]][
                        "data"
                    ].get("correlates_with", "")
                    i["data"]["synonymes"] = dest_onto.jstree_as_dict[i["id"]][
                        "data"
                    ].get("synonymes", "")
                    i["data"]["hex_color"] = dest_onto.jstree_as_dict[i["id"]][
                        "data"
                    ].get("hex_color", "")
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
        """Dump the updated tree to a json file

        Args:
            file_path (str): path to save the json file
        """
        with open(file_path, "w") as fp:
            json.dump(self.jstree_as_dict, fp, indent=4)

    def clean_tree(self) -> list:
        """Clean the tree of non informative fields.

        Returns:
            list: return the updated tree as list of dict (json)
        """
        clean_tree_list = []
        for i in self.jstree_as_dict:
            clean_tree_list.append(self.jstree_as_dict[i])
        self.jstree_as_list = clean_tree_list
        return self.jstree_as_list
