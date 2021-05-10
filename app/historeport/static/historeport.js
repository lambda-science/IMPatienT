var input = document.querySelector("input[id=synonymes]");
var input_tag = new Tagify(input);
var input2 = document.querySelector("input[id=gene]");
var input2_tag = new Tagify(input2);
var data_url = $("#data-url").data();

var json_tree = $("input[id=ontology_tree]").val();
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
    data.node.data = { synonymes: "", genes: "", description: "" };
    $("#jstree").jstree().set_id(data.node, newId);
  })
  .jstree({
    core: {
      check_callback: true,
      data: JSON.parse(json_tree),
    },
    // plugins: ["contextmenu", "wholerow", "unique", "search", "changed", "dnd"],
    plugins: ["wholerow", "unique", "search", "changed"],
    //contextmenu: {
    //  items: function ($node) {
    //    return {
    //      Create: {
    //        separator_before: false,
    //        separator_after: false,
    //        label: "Create",
    //        action: function (obj) {
    //          $node = $("#jstree").jstree().create_node($node);
    //          $("#jstree").jstree().edit($node);
    //        },
    //      },
    //    };
    //  },
    //},
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
  $("input[id=preabsProba]").val(data.node.data.presence || -0.25);
  set_slider_span(data.node.data.presence || "-0.25");
});

$("input[id=preabsProba]").on("input change", function () {
  set_slider_span($("input[id=preabsProba]").val());
  update_node_data();
});

// placeholder
function update_node_data() {
  var node_id = $("#jstree").jstree(true).get_selected();
  var node = $("#jstree").jstree(true).get_node(node_id);
  node.data.presence = $("input[id=preabsProba]").val();
  if ($("input[id=preabsProba]").val() > "0") {
    $("#jstree").jstree(true).set_icon(node, "/static/checkmark-32.png");
  } else if ($("input[id=preabsProba]").val() === "0") {
    $("#jstree").jstree(true).set_icon(node, "/static/x-mark-32.png");
  } else if ($("input[id=preabsProba]").val() < "0") {
    $("#jstree").jstree(true).set_icon(node, "/static/question-mark-16.png");
  } else {
    $("#jstree").jstree(true).set_icon(node, true);
  }
  var v = $("#jstree").jstree(true).get_json("#", { flat: true });
  $("input[id=ontology_tree]").val(JSON.stringify(v));
  predict_diag();
}

function set_slider_span(slide_value) {
  var message = {
    //"-1.25":
    //  '<span class="badge bg-danger range-value">No Info: Not Askable (-1.25)</span>',
    //"-1":
    //  '<span class="badge bg-warning range-value">No Info: Difficile (-1)</span>',
    //"-0.75":
    //  '<span class="badge bg-warning range-value">No Info: Modéré (-0.75)</span>',
    //"-0.5":
    //  '<span class="badge bg-warning range-value">No Info: Facile (-0.5)</span>',
    "-0.25":
      '<span class="badge bg-warning range-value">No Info (-0.25)</span>',
    0: '<span class="badge bg-danger range-value">Absent (0)</span>',
    0.25: '<span class="badge bg-success range-value">Présent Faible (0.25)</span>',
    0.5: '<span class="badge bg-success range-value">Présent Modéré (0.5)</span>',
    0.75: '<span class="badge bg-success range-value">Présent Fort (0.75)</span>',
    1: '<span class="badge bg-success range-value">Présent Total (1)</span>',
  };
  $("#sliderspan").html(message[slide_value]);
}

function predict_diag() {
  var json_tree = $("input[id=ontology_tree]").val();
  $.ajax({
    type: "POST",
    url: data_url.predict,
    data: json_tree,
    success: function (data) {
      var results = JSON.parse(data);
      $("div.predict_diag").html("Class: " + results.class);
      $("div.predict_proba").html("Probability: " + results.proba);
    },
    dataType: "text",
  });
}
