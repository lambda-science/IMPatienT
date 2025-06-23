import base64
import io
import json
import os
import pickle  # nosec
import traceback
from urllib import parse

import PIL.Image
import dash
import dash_bootstrap_components as dbc
import numpy as np
from dash import html
from dash.dependencies import Input, Output, State
from flask import current_app
from joblib import Memory
from skimage import io as skio

import impatient.app.dashapp.common_func as common_func
import impatient.app.dashapp.plot_common as plot_common
from impatient.app import db
from impatient.app.dashapp.shapes_to_segmentations import (
    compute_segmentations,
    blend_image_and_classified_regions_pil,
)
from impatient.app.dashapp.trainable_segmentation import multiscale_basic_features
from impatient.app.models import Image

memory = Memory("./joblib_cache", verbose=1)
compute_features = memory.cache(multiscale_basic_features)

onto_tree_imgannot = common_func.load_onto()
class_label_colormap = {
    int(term["id"].split(":")[1]): term["data"]["hex_color"]
    for term in onto_tree_imgannot
    if term["data"]["image_annotation"] is True
}
class_labels = [
    int(term["id"].split(":")[1])
    for term in onto_tree_imgannot
    if term["data"]["image_annotation"] is True
]
button_list = [
    int(i["id"].split(":")[1])
    for i in onto_tree_imgannot
    if i["data"]["image_annotation"] is True
]
NUM_LABEL_CLASSES = len(class_label_colormap)
DEFAULT_LABEL_CLASS = class_labels[0]

# we can't have less colors than classes
assert NUM_LABEL_CLASSES <= len(class_label_colormap)  # nosec


def class_to_color(ontology, class_number):
    for term in ontology:
        if int(term["id"].split(":")[1]) == class_number:
            return term["data"]["hex_color"]


def color_to_class(ontology, color_hex):
    for term in ontology:
        if term["data"]["hex_color"] == color_hex:
            return int(term["id"].split(":")[1])


# def class_to_file(seg_matrix, onto_tree_imgannot, save_path):
#     unique_classes = np.unique(seg_matrix)
#     col_df = {"class": [], "color": [], "onto_id": []}
#     for class_img in unique_classes:
#         col_df["class"].append(class_img)
#         col_df["color"].append(onto_tree_imgannot[class_img - 1]["data"]["hex_color"])
#         col_df["onto_id"].append(onto_tree_imgannot[class_img - 1]["id"])
#     df = pd.DataFrame.from_dict(col_df)
#     df.to_csv(save_path, index=False)


def make_default_figure(
    images=None,
    stroke_color="",
    stroke_width=3,
    shapes=[],
    source_img=None,
):
    fig = plot_common.dummy_fig()
    plot_common.add_layout_images_to_fig(fig, images)
    fig.update_layout(
        {
            "dragmode": "drawopenpath",
            "shapes": shapes,
            "newshape.line.color": stroke_color,
            "newshape.line.width": stroke_width,
            "margin": dict(l=0, r=0, b=0, t=0, pad=4),
        }
    )
    if source_img:
        fig._layout_obj.images[0].source = source_img
    return fig


# Converts image classifier to a JSON compatible encoding and creates a
# dictionary that can be downloaded
# see use_ml_image_segmentation_classifier.py
def save_img_classifier(clf, label_to_colors_args, segmenter_args):
    clfbytes = io.BytesIO()
    pickle.dump(clf, clfbytes)
    clfb64 = base64.b64encode(clfbytes.getvalue()).decode()
    return {
        "classifier": clfb64,
        "segmenter_args": segmenter_args,
        "label_to_colors_args": label_to_colors_args,
    }


def show_segmentation(
    image_path,
    mask_shapes,
    features,
    segmenter_args,
    class_label_colormap,
    onto_tree_imgannot,
):
    """adds an image showing segmentations to a figure's layout"""
    # add 1 because classifier takes 0 to mean no mask
    # shape_layers = [
    #    color_to_class(class_label_colormap, shape["line"]["color"]) + 1
    #    for shape in mask_shapes
    # ]
    shape_layers = [
        color_to_class(onto_tree_imgannot, shape["line"]["color"])
        for shape in mask_shapes
    ]
    label_to_colors_args = {
        "colormap": class_label_colormap,
        "color_class_offset": 0,
    }
    segimg, seg_matrix, clf = compute_segmentations(
        mask_shapes,
        img_path=image_path,
        shape_layers=shape_layers,
        label_to_colors_args=label_to_colors_args,
        features=features,
    )
    # get the classifier that we can later store in the Store
    classifier = save_img_classifier(clf, label_to_colors_args, segmenter_args)
    segimgpng = plot_common.img_array_to_pil_image(segimg)
    return (segimgpng, seg_matrix, classifier)


def register_callbacks(dashapp):
    """ " """

    @dashapp.callback(
        [
            Output("graph", "figure"),
            Output("masks", "data"),
            Output("classifier-store", "data"),
            Output("classified-image-store", "data"),
            Output("alertbox", "children"),
            Output("sigma-range-slider", "value"),
        ],
        [
            Input("url", "href"),
            Input("graph", "relayoutData"),
            Input(
                {"type": "label-class-button", "index": dash.dependencies.ALL},
                "n_clicks_timestamp",
            ),
            Input("stroke-width", "value"),
            Input("show-segmentation", "value"),
            Input("download-button", "n_clicks"),
            Input("sigma-range-slider", "value"),
        ],
        [
            State("masks", "data"),
        ],
    )
    def annotation_react(
        href,
        graph_relayoutData,
        any_label_class_button_value,
        stroke_width_value,
        show_segmentation_value,
        download_button_n_clicks,
        sigma_range_slider_value,
        masks_data,
    ):
        classified_image_store_data = dash.no_update
        classifier_store_data = dash.no_update
        alertbox = html.Div()
        cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
        # print(cbcontext)
        # Ugly Source Building to Refactor
        key_params = dict(parse.parse_qsl(parse.urlsplit(href).query))
        url_splited = parse.urlsplit(href)
        image = Image.query.get(key_params["id"])
        image_split_path = image.image_background_path.split("/")
        img = skio.imread(image.image_path)
        source = "/".join(
            [
                "http:/",
                url_splited.netloc,
                "data",
                "images",
                image_split_path[-2],
                image_split_path[-1],
            ]
        )
        if cbcontext == "url.href":
            if image.mask_annot_path is not None and image.mask_annot_path != []:
                with open(image.mask_annot_path, "r") as file:
                    masks_data["shapes"] = json.load(file)
                    sigma_range_slider_value = [
                        image.sigma_range_min,
                        image.sigma_range_max,
                    ]

        if cbcontext in ["sigma-range-slider.value"] or (
            ("Show segmentation" in show_segmentation_value)
            and (len(masks_data["shapes"]) > 0)
        ):
            segmentation_features_dict = {
                "intensity": True,
                "edges": True,
                "texture": True,
            }
            features = compute_features(
                img,
                **segmentation_features_dict,
                sigma_min=sigma_range_slider_value[0],
                sigma_max=sigma_range_slider_value[1],
            )
        if cbcontext == "graph.relayoutData":
            if "shapes" in graph_relayoutData.keys():
                masks_data["shapes"] = graph_relayoutData["shapes"]
            else:
                return dash.no_update
        stroke_width = int(round(2 ** (stroke_width_value)))
        # find label class value by finding button with the most recent click
        if any_label_class_button_value is None:
            label_class_value = DEFAULT_LABEL_CLASS
        else:
            label_class_value = button_list[
                max(
                    enumerate(any_label_class_button_value),
                    key=lambda t: 0 if t[1] is None else t[1],
                )[0]
            ]
            # label_class_value = class_labels[label_class_value]
        fig = make_default_figure(
            images=[image.image_path],
            stroke_color=class_to_color(onto_tree_imgannot, label_class_value),
            stroke_width=stroke_width,
            shapes=masks_data["shapes"],
            source_img=source,
        )

        # We want the segmentation to be computed
        if ("Show segmentation" in show_segmentation_value) and (
            len(masks_data["shapes"]) > 0
        ):
            segimgpng = None
            try:
                feature_opts = dict(
                    segmentation_features_dict=segmentation_features_dict
                )
                feature_opts["sigma_min"] = sigma_range_slider_value[0]
                feature_opts["sigma_max"] = sigma_range_slider_value[1]
                segimgpng, seg_matrix, clf = show_segmentation(
                    image.image_path,
                    masks_data["shapes"],
                    features,
                    feature_opts,
                    class_label_colormap,
                    onto_tree_imgannot,
                )
                if cbcontext == "download-button.n_clicks":
                    classifier_store_data = clf
                    classified_image_store_data = plot_common.pil_image_to_uri(
                        blend_image_and_classified_regions_pil(
                            PIL.Image.open(image.image_path), segimgpng
                        )
                    )
                    image.sigma_range_min = sigma_range_slider_value[0]
                    image.sigma_range_max = sigma_range_slider_value[1]
                    image.seg_matrix_path = os.path.join(
                        current_app.config["IMAGES_FOLDER"],
                        image.patient_id,
                        image.image_name + "_seq_matrix.npy",
                    )
                    image.mask_annot_path = os.path.join(
                        current_app.config["IMAGES_FOLDER"],
                        image.patient_id,
                        image.image_name + "_mask_annot.json",
                    )
                    np.save(image.seg_matrix_path, seg_matrix)
                    image.mask_image_path = os.path.join(
                        current_app.config["IMAGES_FOLDER"],
                        image.patient_id,
                        image.image_name + "_mask_image.png",
                    )
                    segimgpng.save(image.mask_image_path)
                    image.blend_image_path = os.path.join(
                        current_app.config["IMAGES_FOLDER"],
                        image.patient_id,
                        image.image_name + "_blend_image.png",
                    )
                    blend_image_and_classified_regions_pil(
                        PIL.Image.open(image.image_path), segimgpng
                    ).save(image.blend_image_path)
                    image.classifier_path = os.path.join(
                        current_app.config["IMAGES_FOLDER"],
                        image.patient_id,
                        image.image_name + "_classifier.pkl",
                    )
                    # image.class_info_path = os.path.join(
                    #     current_app.config["IMAGES_FOLDER"],
                    #     image.patient_id,
                    #     image.image_name + "_class_info.csv",
                    # )
                    # class_to_file(seg_matrix, onto_tree_imgannot, image.class_info_path)
                    with open(image.mask_annot_path, "w") as file:
                        json.dump(masks_data["shapes"], file, indent=4)
                    with open(image.classifier_path, "wb") as file:
                        pickle.dump(clf, file)
                    db.session.commit()
                    alertbox = dbc.Alert("Annotation Saved to Database !", color="info")

            except Exception:
                print(traceback.format_exc())
                alertbox = dbc.Alert(
                    "Issues Saving to Database Please Reload The Page...", color="error"
                )
            images_to_draw = []
            if segimgpng is not None:
                images_to_draw = [segimgpng]
            fig = plot_common.add_layout_images_to_fig(fig, images_to_draw)
        fig.update_layout(uirevision="segmentation")
        return (
            fig,
            masks_data,
            classifier_store_data,
            classified_image_store_data,
            alertbox,
            sigma_range_slider_value,
        )
