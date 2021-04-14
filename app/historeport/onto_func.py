def update_from_template(old_json, template_json):
    """Function to update the current ontology tree used for anotation with latest
    modifications to the template of the ontology tree (delete, update, create new)"""
    new_json = []
    template_as_dict = {
        i["id"]: {
            "id": i["id"],
            "text": i["text"],
            "icon": i["icon"],
            "data": i["data"],
            "parent": i["parent"],
        }
        for i in template_json
    }
    old_json_as_dict = {
        i["id"]: {
            "id": i["id"],
            "text": i["text"],
            "icon": i["icon"],
            "data": i["data"],
            "parent": i["parent"],
        }
        for i in old_json
    }
    for i in old_json:
        if i["id"] not in template_as_dict.keys():
            # Si l'ID n'est plus dans le template il devient OUTDATED
            i["data"]["outdated"] = True
            if "OUTDATED" not in i["text"]:
                i["text"] = "OUTDATED : " + i["text"]
            new_json.append(i)
        elif i["id"] in template_as_dict.keys():
            if (
                i["text"] != template_as_dict[i["id"]]["text"]
                or i["data"] != template_as_dict[i["id"]]["data"]
            ):
                # Si le nom ou les data sont modifiées: on mets à jour
                i["data"].setdefault("old_name", []).append(i["text"])
                i["text"] = template_as_dict[i["id"]]["text"]
                i["data"]["description"] = template_as_dict[i["id"]]["data"].get(
                    "description", ""
                )
                i["data"]["genes"] = template_as_dict[i["id"]]["data"].get("genes", "")
                i["data"]["synonymes"] = template_as_dict[i["id"]]["data"].get(
                    "synonymes", ""
                )
            new_json.append(i)
    for i in template_as_dict.keys():
        if i not in old_json_as_dict.keys():
            new_json.append(template_as_dict[i])
    return new_json
