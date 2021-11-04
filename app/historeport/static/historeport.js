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

var json_tree = $("input[id=ontology_tree]").val();
function ontology_ID(id_list) {
  id = id_list.sort()[id_list.length - 2].substring(4);
  id = parseInt(id);
  id += 1;
  id = "MHO" + id.toString().padStart(6, "0");
  return id;
}

$("#jstree")
  .bind("create_node.jstree", function (event, data) {
    var v = $("#jstree").jstree(true).get_json("#", { flat: true });
    var id_list = v.map(({ id }) => id);
    var newId = ontology_ID(id_list);
    var randomColor = Math.floor(Math.random() * 16777215).toString(16);
    // data.node.data = { description: "", genes: "", synonymes: "", phenotype: "", phenotype_datamined: "", gene_datamined: "", alternative_language: "", correlates_with: "" };
    data.node.data = {
      description: "",
      synonymes: "",
      phenotype_datamined: "",
      gene_datamined: "",
      alternative_language: "",
      correlates_with: "",
      hex_color: "#" + randomColor,
    };
    $("#jstree").jstree().set_id(data.node, newId);
  })
  .jstree({
    core: {
      check_callback: true,
      data: JSON.parse(json_tree),
    },
    // plugins: ["contextmenu", "wholerow", "unique", "search", "changed", "dnd"],
    plugins: ["wholerow", "unique", "search", "changed", "sort"],
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
update_annotated_terms_overview();

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
  $("input[id=preabsProba]").val(data.node.data.presence || -0.25);
  set_slider_span(data.node.data.presence || "-0.25");
});

$("input[id=preabsProba]").on("input change", function () {
  set_slider_span($("input[id=preabsProba]").val());
  update_node_data();
  update_annotated_terms_overview();
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
}

function update_annotated_terms_overview() {
  // var v = $("#jstree").jstree(true).get_json("#", { flat: true });
  var v = JSON.parse($("input[id=ontology_tree]").val());
  var present_features = [];
  var absent_features = [];
  for (const [key, value] of Object.entries(v)) {
    if (value.data.presence > "0") {
      present_features.push(value.id + " " + value.text);
    } else if (value.data.presence === "0") {
      absent_features.push(value.id + " " + value.text);
    }
    let present_feat_overview = document.getElementById("feature-present");
    let absent_feat_overview = document.getElementById("feature-absent");
    present_feat_overview.innerHTML = "";
    absent_feat_overview.innerHTML = "";
    for (const [key, value] of Object.entries(present_features)) {
      present_feat_overview.innerHTML +=
        "<span style='color:green'>" + value + "</span></br>";
    }
    for (const [key, value] of Object.entries(absent_features)) {
      absent_feat_overview.innerHTML +=
        "<span style='color:red'>" + value + "</span></br>";
    }
  }
}

function set_slider_span(slide_value) {
  var message = {
    "-0.25": '<span class="badge bg-warning range-value">N/A</span>',
    0: '<span class="badge bg-danger range-value">Absent</span>',
    0.25: '<span class="badge bg-success range-value">Present (Low)</span>',
    0.5: '<span class="badge bg-success range-value">Present (Moderate)</span>',
    0.75: '<span class="badge bg-success range-value">Present (High)</span>',
    1: '<span class="badge bg-success range-value">Present (Total)</span>',
  };
  $("#sliderspan").html(message[slide_value]);
}

function predict_diag_boqa() {
  var json_tree = $("input[id=ontology_tree]").val();
  $.ajax({
    type: "POST",
    url: data_url.boqa,
    data: json_tree,
    success: function (data) {
      var results = JSON.parse(data);
      $("div.predict_diag_boqa").html("Class: " + results.class);
      $("div.predict_proba_boqa").html("Probability: " + results.proba);
    },
    dataType: "text",
  });
}
$("#predictbutton").on("click", function () {
  predict_diag_boqa();
});

$(function () {
  $("#upload-file-btn").click(function () {
    var form_data = new FormData($("#upload-file")[0]);
    form_data.append(
      "lang",
      $("#select-ocr-lang").find("option:selected").val()
    );
    console.log(form_data);
    $.ajax({
      type: "POST",
      url: "/ocr_pdf",
      data: form_data,
      contentType: false,
      cache: false,
      processData: false,
      success: function (data) {
        console.log("sucess !");
        let text_results_field = document.querySelector("div.context");
        text_results_field.innerHTML = "";
        var instance = new Mark(document.querySelector("div.context"));
        let json_ans = JSON.parse(data);
        let accordion = document.getElementById("divAccordion");
        accordion.removeAttribute("hidden");
        options_pos = {
          element: "markpos",
          separateWordSearch: false,
          accurarcy: "exactly",
          ignorePunctuation: ":;.,-–—‒_(){}[]!'\"+=".split(""),
        };
        options_neg = {
          element: "markneg",
          separateWordSearch: false,
          accurarcy: "exactly",
          ignorePunctuation: ":;.,-–—‒_(){}[]!'\"+=".split(""),
        };
        for (const [key, value] of Object.entries(json_ans.results.full_text)) {
          text_results_field.innerHTML += value + "</br>";
        }
        var keywords_pos = [];
        var keywords_neg = [];
        for (const [key, value] of Object.entries(
          json_ans.results.match_list
        )) {
          if (value[0] == 1) {
            keywords_pos.push(value[1]);
          } else if (value[0] == 0) {
            keywords_neg.push(value[1]);
          }
        }
        instance.mark(keywords_pos, options_pos);
        instance.mark(keywords_neg, options_neg);
        console.log("marked !");
      },
    });
  });
});
