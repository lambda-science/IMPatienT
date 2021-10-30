var data_url = $("#data-url").data();
var input = document.querySelector("input[id=synonymes]");
var input_tag = new Tagify(input);
// var input2 = document.querySelector("input[id=gene]");
// var input2_tag = new Tagify(input2);
var input3 = document.querySelector("input[id=gene_datamined]");
var input3_tag = new Tagify(input3);
// var input4 = document.querySelector("input[id=phenotype]");
// var input4_tag = new Tagify(input4);
var input5 = document.querySelector("input[id=phenotype_datamined]");
var input5_tag = new Tagify(input5);
var input6 = document.querySelector("input[id=alternative_language]");
var input6_tag = new Tagify(input6);
var input7 = document.querySelector("input[id=correlates_with]");
var input7_tag = new Tagify(input7);

function ontology_ID(id_list) {
  id = id_list.sort()[id_list.length - 2].substring(4);
  id = parseInt(id);
  id += 1;
  id = "MHO" + id.toString().padStart(6, "0");
  return id
};

$("#jstree")
  .bind("create_node.jstree", function (event, data) {
    var v = $("#jstree").jstree(true).get_json("#", { flat: true });
    var id_list = v.map(({ id }) => id);
    var newId = ontology_ID(id_list);
    var randomColor = Math.floor(Math.random() * 16777215).toString(16);
    // data.node.data = { description: "", genes: "", synonymes: "", phenotype: "", phenotype_datamined: "", gene_datamined: "", alternative_language: "", correlates_with: "" };
    data.node.data = { description: "", synonymes: "", phenotype_datamined: "", gene_datamined: "", alternative_language: "", correlates_with: "", hex_color: "#" + randomColor };
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
    plugins: ["contextmenu", "dnd", "wholerow", "unique", "search", "changed", "sort"],
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
  // input2_tag.removeAllTags();
  // input2_tag.addTags(data.node.data.genes);
  input3_tag.removeAllTags();
  input3_tag.addTags(data.node.data.gene_datamined);
  // input4_tag.removeAllTags();
  // input4_tag.addTags(data.node.data.phenotype);
  input5_tag.removeAllTags();
  input5_tag.addTags(data.node.data.phenotype_datamined);
  input6_tag.removeAllTags();
  input6_tag.addTags(data.node.data.alternative_language);
  input7_tag.removeAllTags();
  input7_tag.addTags(data.node.data.correlates_with);
  $("textarea[id=description]").val(data.node.data.description) || "";
});

// Register form data to JSON file
function update_node_data() {
  var node_id = $("#jstree").jstree(true).get_selected();
  var node = $("#jstree").jstree(true).get_node(node_id);
  node.data.synonymes = get_taglist("input[id=synonymes]");
  // node.data.genes = get_taglist("input[id=gene]");
  node.data.gene_datamined = get_taglist("input[id=gene_datamined]");
  // node.data.phenotype = get_taglist("input[id=phenotype]");
  node.data.phenotype_datamined = get_taglist("input[id=phenotype_datamined]");
  node.data.alternative_language = get_taglist("input[id=alternative_language]");
  node.data.correlates_with = get_taglist("input[id=correlates_with]");
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
