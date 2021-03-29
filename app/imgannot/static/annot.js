var dzi_url = $("#dzi-url").data();
var viewer = OpenSeadragon({
  id: "seadragon-viewer",
  prefixUrl:
    "https://cdn.jsdelivr.net/npm/openseadragon@2.4/build/openseadragon/images/",
  tileSources: dzi_url.url,
  animationTime: 0.1,
  alwaysBlend: true,
  maxZoomPixelRatio: 3,
  minZoomLevel: 0.5,
  visibilityRatio: 0.1,
  zoomPerScroll: 1.8,
  showNavigator: true,
  navigatorBackground: "#000",
});

// Initialize the Annotorious plugin
var anno = OpenSeadragon.Annotorious(viewer, {
  widgets: [{ widget: "TAG", vocabulary: ["test", "test2"] }],
});

// Load annotations from Form data
var my_annot_json = JSON.parse($("input[id=annotation_json]").val() || "[]");
for (const element of my_annot_json) {
  anno.addAnnotation(element);
}

// Handler to create annot
anno.on("createAnnotation", function (annotation) {
  var my_annot_json = JSON.parse($("input[id=annotation_json]").val() || "[]");
  my_annot_json.push(annotation);
  $("input[id=annotation_json]").val(JSON.stringify(my_annot_json));
});

// Handler to update annot
anno.on("updateAnnotation", function (annotation) {
  var my_annot_json = JSON.parse($("input[id=annotation_json]").val());
  var new_annot_json = [];
  for (const element of my_annot_json) {
    if (element.id === annotation.id) {
      new_annot_json.push(annotation);
    } else {
      new_annot_json.push(element);
    }
  }
  $("input[id=annotation_json]").val(JSON.stringify(new_annot_json));
});

// Handler to delete annot
anno.on("deleteAnnotation", function (annotation) {
  var my_annot_json = JSON.parse($("input[id=annotation_json]").val());
  var new_annot_json = [];
  for (const element of my_annot_json) {
    if (element.id === annotation.id) {
      //pass
    } else {
      new_annot_json.push(element);
    }
  }
  $("input[id=annotation_json]").val(JSON.stringify(new_annot_json));
});

// Switch tool (rect or polygon) function
function switch_tool(anno, tool) {
  anno.setDrawingTool(tool);
}

$(document).ready(function () {
  $('[data-toggle="tooltip"]').tooltip();
});
