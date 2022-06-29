// Get data stored in data-url meta tag
var data_url = $("#data-url").data();

// Generate all Tagify object for tag input in the form.
var input = document.querySelector("input[id=synonymes]");
var input_tag = new Tagify(input);
// var input2 = document.querySelector("input[id=gene]");
// var input2_tag = new Tagify(input2);
var input3 = document.querySelector("input[id=gene_datamined]");
var input3_tag = new Tagify(input3);
var input4 = document.querySelector("input[id=hpo_datamined]");
var input4_tag = new Tagify(input4);
var input5 = document.querySelector("input[id=phenotype_datamined]");
var input5_tag = new Tagify(input5);
var input6 = document.querySelector("input[id=alternative_language]");
var input6_tag = new Tagify(input6, { maxTags: 1 });
var input7 = document.querySelector("input[id=correlates_with]");
var input7_tag = new Tagify(input7);

/**
 * Create a new node ID incrementally from all node ID as MHO:XXXXXX
 * @param {array}     id_list   list of all current standard vocabulary terms ID
 * @returns {string}  id        id of the new term
 */
function ontology_ID(id_list) {
  id = id_list.sort()[id_list.length - 2].substring(4);
  id = parseInt(id);
  id += 1;
  id = "MHO:" + id.toString().padStart(6, "0");
  return id;
}

/**
 * Initilize JSTree
 * Load a custom create_node function using our own function and settings default node data
 * Load Data from the data_url.jstree meta tag
 * Activate all required plugins
 */
$("#jstree")
  .bind("create_node.jstree", function (event, data) {
    var v = $("#jstree").jstree(true).get_json("#", { flat: true });
    var id_list = v.map(({ id }) => id);
    var newId = ontology_ID(id_list);
    var randomColor = Math.floor(Math.random() * 16777215).toString(16);
    data.node.data = {
      description: "",
      synonymes: "",
      phenotype_datamined: "",
      gene_datamined: "",
      alternative_language: "",
      correlates_with: "",
      image_annotation: false,
      hex_color: "#" + randomColor,
    };
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
    plugins: ["contextmenu", "dnd", "wholerow", "search", "changed", "sort"],
  });

// Search function for the JSTree search bar
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

// When a JSTree is selected: dynamically update the form about term details.
$("#jstree").on("select_node.jstree", function (e, data) {
  $("input[id=onto_id_ext]").val(data.node.id);
  $("input[id=onto_name]").val(data.node.text);
  $("input[id=parent_id]").val(data.node.parent);
  if (data.node.data.image_annotation) {
    $("input[id=image_annotation]").prop("checked", true);
  } else {
    $("input[id=image_annotation]").prop("checked", false);
  }
  input_tag.loadOriginalValues(data.node.data.synonymes);
  input3_tag.loadOriginalValues(data.node.data.gene_datamined);
  input4_tag.loadOriginalValues(data.node.data.hpo_datamined);
  input5_tag.loadOriginalValues(data.node.data.phenotype_datamined);
  input6_tag.loadOriginalValues(data.node.data.alternative_language);
  input7_tag.loadOriginalValues(data.node.data.correlates_with);

  $("textarea[id=description]").val(data.node.data.description) || "";
});

$("input[id=image_annotation]").change(function () {
  update_node_data();
});

$("input[id=alternative_language]").change(function () {
  update_node_data();
});
$("input[id=synonymes]").change(function () {
  update_node_data();
});
$("textarea[id=description]").change(function () {
  update_node_data();
});

/**
 * When the "update details" button is clicked: update the data of the selected node
 * Get form data, insert it in the JSTree node.data object
 * Call the save_tree function
 */
function update_node_data() {
  var node_id = $("#jstree").jstree(true).get_selected();
  var node = $("#jstree").jstree(true).get_node(node_id);
  node.data.image_annotation = $("input[id=image_annotation]").is(":checked");
  node.data.synonymes = get_taglist("input[id=synonymes]");
  // node.data.genes = get_taglist("input[id=gene]");
  node.data.gene_datamined = get_taglist("input[id=gene_datamined]");
  // node.data.phenotype = get_taglist("input[id=phenotype]");
  node.data.phenotype_datamined = get_taglist("input[id=phenotype_datamined]");
  node.data.alternative_language = get_taglist(
    "input[id=alternative_language]"
  );
  node.data.correlates_with = get_taglist("input[id=correlates_with]");
  node.data.description = $("textarea[id=description]").val();
  $("#jstree").jstree(true).redraw();
  //save_tree();
}
/**
 * Get the current JStree Json data and make an AJAX Request to update the .JSON file
 */
function save_tree() {
  var loading_spinner = document.getElementById("savespinner");
  loading_spinner.removeAttribute("hidden");

  var v = $("#jstree").jstree(true).get_json("#", { flat: true });
  myJSON = JSON.stringify(v);
  $.ajax({
    type: "PATCH",
    url: data_url.savetree,
    data: myJSON,
    success: function (data) {
      loading_spinner.setAttribute("hidden", "true");
    },
    dataType: "text",
  });
}

/**
 * Function to extract the tag list from a given "TagList" input as a string.
 * @param {string} ID of the input tag
 * @returns {string} list of all tags in the input tag separated by ","
 */
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
