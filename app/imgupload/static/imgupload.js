// Orphanet Disease Names Field Handler
// Tagify Field handler with whitelist and Orphanet ajax
var conclusion = document.querySelector("input[id=diagnostic]");
var conclusion_tag = new Tagify(conclusion, {
  enforceWhitelist: true,
  whitelist: [$("input[id=diagnostic]").val(), "UNCLEAR", "HEALTHY", "OTHER"],
  mode: "select",
});

conclusion_tag.on("input", onInputConclusion);

// Tagify AJAX Function to get a list of Orphanet names
var myHeaders_orpha = new Headers({
  apiKey: "ehroes",
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
