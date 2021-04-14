var data_url = $("#data-url").data();
var input = document.querySelector("input[id=synonymes]");
var input_tag = new Tagify(input);
var input2 = document.querySelector("input[id=gene]");
var input2_tag = new Tagify(input2);

function uuidv4() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
    var r = (Math.random() * 16) | 0,
      v = c == "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

$("#jstree")
  .bind("create_node.jstree", function (event, data) {
    var newId = uuidv4();
    $("#jstree").jstree().set_id(data.node, newId);
  })
  .jstree({
    core: {
      check_callback: true,
      data: {
        url: data_url.jstree,
        dataType: "json", // needed only if you do not supply JSON headers
      },
    },
    plugins: ["contextmenu", "dnd", "wholerow", "unique", "search", "hotkeys"],
  });

var to = false;
$("#plugins4_q").keyup(function () {
  if (to) {
    clearTimeout(to);
  }
  to = setTimeout(function () {
    var v = $("#plugins4_q").val();
    $("#jstree").jstree(true).search(v);
  }, 250);
});

// Prefill Form from JSON
$("#jstree").on("select_node.jstree", function (e, data) {
  $("input[id=onto_id_ext]").val(data.node.id);
  $("input[id=onto_name]").val(data.node.text);
  $("input[id=parent_id]").val(data.node.parent);
  input_tag.removeAllTags();
  input_tag.addTags(data.node.data.synonymes);
  input2_tag.removeAllTags();
  input2_tag.addTags(data.node.data.genes);
  $("textarea[id=description]").val(data.node.data.description) || "";
});

// Register form data to JSON file
function update_node_data() {
  var node_id = $("#jstree").jstree(true).get_selected();
  var node = $("#jstree").jstree(true).get_node(node_id);
  node.data.synonymes = get_taglist("input[id=synonymes]");
  node.data.genes = get_taglist("input[id=gene]");
  node.data.description = $("textarea[id=description]").val();
  save_tree();
}
function save_tree() {
  var v = $("#jstree").jstree(true).get_json("#", { flat: true });
  myJSON = JSON.stringify(v);
  $.ajax({
    type: "PATCH",
    url: data_url.savetree,
    data: myJSON,
    success: console.log("Ontology File Updated"),
    dataType: "text",
  });
}

function get_taglist(input_id) {
  list_tag = [];
  if ($(input_id).val() === "") {
    return "";
  } else {
    var tag = JSON.parse($(input_id).val());
    for (var obj in tag) {
      list_tag.push(tag[obj].value);
    }
    return list_tag.toString();
  }
}
