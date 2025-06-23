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

// HPO Terms Field Handler
// Tagify Field handler with whitelist and HPO ajax
var pheno_terms = document.querySelector("input[id=pheno_terms]");
var pheno_terms_tag = new Tagify(pheno_terms, {
  enforceWhitelist: true,
  whitelist: $("input[id=pheno_terms]").val().split(","),
}); // for aborting the call

pheno_terms_tag.on("input", onInputHPO);

// Tagify AJAX Function to get a list of HPO terms
var delayTimer;
function onInputHPO(e) {
  pheno_terms_tag.whitelist = null; // reset the whitelist
  // show loading animation and hide the suggestions dropdown
  pheno_terms_tag.loading(true).dropdown.hide();
  clearTimeout(delayTimer);

  delayTimer = setTimeout(function () {
    var value = e.detail.value;
    fetch(
      "https://hpo.jax.org/api/hpo/search/?q=" +
        value +
        "&max=5&offset=0&category=terms"
    )
      .then((RES) => RES.json())
      .then(function (newWhitelist) {
        var terms_list = [];
        for (var i = 0; i < newWhitelist.terms.length; i++) {
          terms_list.push(
            newWhitelist.terms[i]["id"] + " " + newWhitelist.terms[i]["name"]
          );
        }
        pheno_terms_tag.whitelist = terms_list;
        pheno_terms_tag.loading(false);
        pheno_terms_tag.dropdown.show(); // render the suggestions dropdown
      });
  }, 700);
}

var gene_diag_tag = new Tagify(gene_diag, {
  enforceWhitelist: true,
  whitelist: [$("input[id=gene_diag]").val()],
  mode: "select",
});
gene_diag_tag.on("input", onInputGene);

// Tagify AJAX Function to get a list of HPO terms
var delayTimer;
function onInputGene(e) {
  gene_diag_tag.whitelist = null; // reset the whitelist
  // show loading animation and hide the suggestions dropdown
  gene_diag_tag.loading(true).dropdown.hide();
  clearTimeout(delayTimer);
  var myHeaders = new Headers({
    accept: "application/json",
  });
  var options = {
    method: "GET",
    headers: myHeaders,
  };
  delayTimer = setTimeout(function () {
    var value = e.detail.value;
    fetch(
      "https://rest.genenames.org/search/symbol/" +
        value +
        "*+AND+status:Approved",
      options
    )
      .then((RES) => RES.json())
      .then(function (newWhitelist) {
        var terms_list = [];
        var response = newWhitelist.response.docs;
        console.log(newWhitelist);

        for (var i = 0; i < response.length; i++) {
          terms_list.push(response[i]["hgnc_id"] + " " + response[i]["symbol"]);
        }
        gene_diag_tag.whitelist = terms_list;
        gene_diag_tag.loading(false);
        gene_diag_tag.dropdown.show(); // render the suggestions dropdown
      });
  }, 700);
}

// Orphanet Disease Names Field Handler
// Tagify Field handler with whitelist and Orphanet ajax
var conclusion = document.querySelector("input[id=conclusion]");
var conclusion_tag = new Tagify(conclusion, {
  enforceWhitelist: true,
  whitelist: [$("input[id=conclusion]").val(), "UNCLEAR", "HEALTHY", "OTHER"],
  mode: "select",
});

conclusion_tag.on("input", onInputConclusion);

// Tagify AJAX Function to get a list of Orphanet names
var myHeaders_orpha = new Headers({
  apiKey: "impatient",
});
var options_orpha = {
  headers: myHeaders_orpha,
};

var delayTimer;
function onInputConclusion(e) {
  conclusion_tag.whitelist = null; // reset the whitelist
  // show loading animation and hide the suggestions dropdown
  conclusion_tag.loading(true).dropdown.hide();
  clearTimeout(delayTimer);
  delayTimer = setTimeout(function () {
    var value = e.detail.value;

    fetch(
      "https://api.orphacode.org/EN/ClinicalEntity/ApproximateName/" + value,
      options_orpha
    )
      .then((RES) => RES.json())
      .then(function (newWhitelist) {
        var terms_list = [];
        for (var i = 0; i < newWhitelist.length; i++) {
          terms_list.push(
            "ORPHA:" +
              newWhitelist[i]["ORPHAcode"] +
              " " +
              newWhitelist[i]["Preferred term"]
          );
        }
        terms_list.push("UNCLEAR", "HEALTHY", "OTHER");
        conclusion_tag.whitelist = terms_list;
        conclusion_tag.loading(false);
        conclusion_tag.dropdown.show(); // render the suggestions dropdown
      });
  }, 700);
}

// Get the JSON of the JSTree (stored in hidden form input) as a variable.
var json_tree = $("input[id=ontology_tree]").val();

/**
 * Create a new node ID incrementally from all node ID as MHO:XXXXXX
 * @param {array}     id_list   list of all current standard vocabulary terms ID
 * @returns {string}  id        id of the new term
 */
function ontology_ID(id_list) {
  id = id_list.sort()[id_list.length - 2].substring(4);
  id = parseInt(id);
  id += 1;
  id = "MHO" + id.toString().padStart(6, "0");
  return id;
}

/**
 * Initilize JSTree
 * Load a custom create_node function using our own function and settings default node data
 * Load Data from the json_tree variable (hidden input form)
 * Activate all required plugins
 */
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
      hex_color: randomColor,
    };
    $("#jstree").jstree().set_id(data.node, newId);
  })
  .jstree({
    core: {
      check_callback: true,
      data: JSON.parse(json_tree),
    },
    // plugins: ["contextmenu", "wholerow", "unique", "search", "changed", "dnd"],
    plugins: ["wholerow", "search", "changed", "sort"],
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

// Call update_annotated_terms_overview function when page is loaded the first time
update_annotated_terms_overview();

// When a JSTree is selected: dynamically update the form about term details.
$("#jstree").on("select_node.jstree", function (e, data) {
  $("input[id=onto_id_ext]").val(data.node.id);
  $("input[id=onto_name]").val(data.node.text);
  $("input[id=parent_id]").val(data.node.parent);
  input_tag.loadOriginalValues(data.node.data.synonymes);
  input3_tag.loadOriginalValues(data.node.data.gene_datamined);
  input4_tag.loadOriginalValues(data.node.data.hpo_datamined);
  input5_tag.loadOriginalValues(data.node.data.phenotype_datamined);
  input6_tag.loadOriginalValues(data.node.data.alternative_language);
  input7_tag.loadOriginalValues(data.node.data.correlates_with);
  $("textarea[id=description]").val(data.node.data.description) || "";
  // Set slider value from node data or set default value (-0.25)
  $("input[id=preabsProba]").val(data.node.data.presence || -0.25);
  set_slider_span(data.node.data.presence || "-0.25");
});

// When the slider value change for a node: update JSTree node data and terms overview div.
$("input[id=preabsProba]").on("input change", function () {
  // Set slider visual
  set_slider_span($("input[id=preabsProba]").val());
  // Update node data and overview div
  update_node_data();
  update_annotated_terms_overview();
});

/**
 * Function to update the Node Data with the value of the slider also change its icon.
 * Get form data, insert it in the JSTree node.data object
 * Call the save_tree function
 */
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

/**
 * Function to update the overview div in the HTML page (summary of all terms annotated)
 * Iterate on all nodes of the JSTree. If the data of presence is different from -0.25,
 * add the term to the corresponding list (present or absent/negated).
 * For each elem of each list, add a new span to the HTLM div with the Node ID and name
 */
function update_annotated_terms_overview() {
  // var v = $("#jstree").jstree(true).get_json("#", { flat: true });
  var v = JSON.parse($("input[id=ontology_tree]").val());
  var present_features = [];
  var absent_features = [];
  for (const [key, value] of Object.entries(v)) {
    presence_value = value.data.presence || -0.25;
    if (presence_value > "0") {
      present_features.push(value.id + " " + value.text);
    } else if (presence_value === "0") {
      absent_features.push(value.id + " " + value.text);
    }
    var present_feat_overview = document.getElementById("feature-present");
    var absent_feat_overview = document.getElementById("feature-absent");
    present_feat_overview.innerHTML = "";
    absent_feat_overview.innerHTML = "";
  }
  for (const [key, value] of Object.entries(present_features)) {
    present_feat_overview.innerHTML +=
      "<span style='color:green'>" + value + "</span><br />";
  }
  for (const [key, value] of Object.entries(absent_features)) {
    absent_feat_overview.innerHTML +=
      "<span style='color:red'>" + value + "</span><br />";
  }
}

/**
 * Function to set the slider sub-text according to the slider value
 * @param {float} value - the value of the slider
 */
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
/**
 * Function to get BOQA diagnosis suggestions for query JSTree.
 * This function make an AJAX request with que JSTree as JSON data.
 * If sucessful, it updates the prediction HTML div with the results. (class and proba)
 */
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
// Trigger the Prediction AJAX Function when clicking the predict button
$("#predictbutton").on("click", function () {
  predict_diag_boqa();
});

/**
 * Function used for the OCR/NLP analysis (first part of the form)
 *
 * On file upload, show a loading animation and make an AJAX request to the server.
 * If successful analysis, create a Mark.JS instance and configure it for positive and
 * negative instance.
 * For each line in the detected text, add it to the text viewer.
 * From the results JSON, extract the results in two list: one for present and one for
 * absent (negated) terms.
 * For each entry in the lists, mark it in the text viewer using Mark.JS
 * and fill the two accordions with the marking results.
 * Finally update the JSTree with the results from the analysis: set node data presence
 * to 0 or 1 depending on positive or negated detection.
 * And update the final annotation overview.
 */
$(function () {
  $("#upload-file-btn").click(function () {
    var loading_spinner = document.getElementById("ocr-loading");
    var fail_div = document.getElementById("ocr-fail");
    loading_spinner.removeAttribute("hidden");
    var form_data = new FormData($("#upload-file")[0]);
    form_data.append(
      "language",
      $("#select-ocr-lang").find("option:selected").val()
    );
    // On file upload, show a loading animation and make an AJAX request to the server.
    $.ajax({
      type: "POST",
      url: "/ocr_pdf",
      data: form_data,
      contentType: false,
      cache: false,
      processData: false,
      error: function (data) {
        fail_div.removeAttribute("hidden");
        loading_spinner.setAttribute("hidden", "true");
      },
      // If successful analysis, create a Mark.JS instance and configure it for
      // positive and negative instance.
      success: function (data) {
        fail_div.setAttribute("hidden", "true");
        loading_spinner.setAttribute("hidden", "true");
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
        // For each line in the detected text, add it to the text viewer.
        for (const [key, value] of Object.entries(json_ans.results.full_text)) {
          text_results_field.innerHTML += value + "<br />";
        }

        // From the results JSON, extract the results in two list: one for present and
        // one for absent (negated) terms.
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

        // For each entry in the lists, mark it in the text viewer using Mark.JS
        // and fill the two accordions with the marking results.
        instance.mark(keywords_pos, options_pos);
        instance.mark(keywords_neg, options_neg);

        let present_feat_overview_auto = document.getElementById(
          "feature-present-auto"
        );
        let absent_feat_overview_auto = document.getElementById(
          "feature-absent-auto"
        );
        present_feat_overview_auto.innerHTML =
          "ID | Vocab. Term | Pos. in Text | Text | Score<br />";
        absent_feat_overview_auto.innerHTML =
          "ID | Vocab. Term | Pos. in Text | Text | Score<br />";

        // For each entires in our match list add to corresponding accordion
        for (const [key, value] of Object.entries(
          json_ans.results.match_list
        )) {
          if (value[0] == 1) {
            present_feat_overview_auto.innerHTML +=
              "<span style='color:green'>" +
              value[3] +
              " | " +
              value[2] +
              " | " +
              value[5] +
              " | " +
              value[1] +
              " | " +
              value[4] +
              "</span><br />";
          } else if (value[0] == 0) {
            absent_feat_overview_auto.innerHTML +=
              "<span style='color:red'>" +
              value[3] +
              " | " +
              value[2] +
              " | " +
              value[5] +
              " | " +
              value[1] +
              " | " +
              value[4] +
              "</span><br />";
          }

          // Finally update the JSTree with the results from the analysis: set node data
          // presence to 0 or 1 depending on positive or negated detection.
          var json_tree = $("input[id=ontology_tree]").val();
          var json_tree_obj = JSON.parse(json_tree);
          // Iterate the tree and find the node that matches the feature ID
          for (let entry of json_tree_obj) {
            if (entry["id"] == value[3]) {
              if (value[0] == 1) {
                entry["data"]["presence"] = "1";
                entry["icon"] = "/static/checkmark-32.png";
              } else if (value[0] == 0) {
                entry["data"]["presence"] = "0";
                entry["icon"] = "/static/x-mark-32.png";
              }
              $("input[id=ontology_tree]").val(JSON.stringify(json_tree_obj));
            }
          }
        }
        // Update the tree viewer with the latest changes.
        $("#jstree").jstree(true).settings.core.data = json_tree_obj;
        $("#jstree").jstree(true).refresh();

        // Update the final annotation overview.
        update_annotated_terms_overview();
      },
    });
  });
});
