var input = document.querySelector("input[id=synonymes]");
var input_tag = new Tagify(input);
var input2 = document.querySelector("input[id=gene]");
var input2_tag = new Tagify(input2);

var json_tree = $("input[id=ontology_tree]").val();
$("#jstree").jstree({
  core: {
    check_callback: true,
    data: JSON.parse(json_tree),
  },
  plugins: ["wholerow", "unique", "search", "changed"],
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
  if (data.node.data.presence === "1") {
    $("#presence_absence-0").prop("checked", true);
  } else if (data.node.data.presence === "-1") {
    $("#presence_absence-1").prop("checked", true);
  } else if (data.node.data.presence === "0") {
    $("#presence_absence-2").prop("checked", true);
  } else {
    $("#presence_absence-2").prop("checked", true);
  }
});

$("input[name=presence_absence]:checked", "#radio_feature").val(
  update_node_data()
);

// placeholder
function update_node_data() {
  var node_id = $("#jstree").jstree(true).get_selected();
  var node = $("#jstree").jstree(true).get_node(node_id);
  node.data.presence = $(
    "input[name=presence_absence]:checked",
    "#radio_feature"
  ).val();
  if (
    $("input[name=presence_absence]:checked", "#radio_feature").val() === "1"
  ) {
    $("#jstree").jstree(true).set_icon(node, "/static/checkmark-32.png");
  } else if (
    $("input[name=presence_absence]:checked", "#radio_feature").val() === "-1"
  ) {
    $("#jstree").jstree(true).set_icon(node, "/static/x-mark-32.png");
  } else {
    $("#jstree").jstree(true).set_icon(node, true);
  }
  var v = $("#jstree").jstree(true).get_json("#", { flat: true });
  $("input[id=ontology_tree]").val(JSON.stringify(v));
}
