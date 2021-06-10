import dash
from dash.dependencies import Input, Output, State


import app.dashapp.plot_common as plot_common

from app.dashapp.shapes_to_segmentations import (
    compute_segmentations,
    blend_image_and_classified_regions_pil,
)

from app.dashapp.trainable_segmentation import multiscale_basic_features
import io
import base64
import PIL.Image
import os
from app.dashapp import bp
import pickle
from time import time
from joblib import Memory
from skimage import io as skio

memory = Memory("./joblib_cache", bytes_limit=3000000000, verbose=3)

compute_features = memory.cache(multiscale_basic_features)
DEFAULT_LABEL_CLASS = 0
NUM_LABEL_CLASSES = 5
DEFAULT_STROKE_WIDTH = 3  # gives line width of 2^3 = 8
DEFAULT_IMAGE_PATH = os.path.join(bp.static_folder, "segmentation_img.jpg")
DEFAULT_IMAGE_URL = os.path.join(bp.static_url_path, "segmentation_img.jpg")
img = skio.imread(DEFAULT_IMAGE_PATH)
class_label_colormap = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2"]
class_labels = list(range(NUM_LABEL_CLASSES))
# we can't have less colors than classes
assert NUM_LABEL_CLASSES <= len(class_label_colormap)


def class_to_color(n):
    return class_label_colormap[n]


def color_to_class(c):
    return class_label_colormap.index(c)


def make_default_figure(
    images=[DEFAULT_IMAGE_PATH],
    stroke_color=class_to_color(DEFAULT_LABEL_CLASS),
    stroke_width=DEFAULT_STROKE_WIDTH,
    shapes=[],
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


def show_segmentation(image_path, mask_shapes, features, segmenter_args):
    """ adds an image showing segmentations to a figure's layout """
    # add 1 because classifier takes 0 to mean no mask
    shape_layers = [color_to_class(shape["line"]["color"]) + 1 for shape in mask_shapes]
    label_to_colors_args = {
        "colormap": class_label_colormap,
        "color_class_offset": -1,
    }
    segimg, _, clf = compute_segmentations(
        mask_shapes,
        img_path=image_path,
        shape_layers=shape_layers,
        label_to_colors_args=label_to_colors_args,
        features=features,
    )
    # get the classifier that we can later store in the Store
    classifier = save_img_classifier(clf, label_to_colors_args, segmenter_args)
    segimgpng = plot_common.img_array_to_pil_image(segimg)
    return (segimgpng, classifier)


def register_callbacks(dashapp):
    @dashapp.callback(
        [
            Output("graph", "figure"),
            Output("masks", "data"),
            Output("stroke-width-display", "children"),
            Output("classifier-store", "data"),
            Output("classified-image-store", "data"),
        ],
        [
            Input("graph", "relayoutData"),
            Input(
                {"type": "label-class-button", "index": dash.dependencies.ALL},
                "n_clicks_timestamp",
            ),
            Input("stroke-width", "value"),
            Input("show-segmentation", "value"),
            Input("download-button", "n_clicks"),
            Input("download-image-button", "n_clicks"),
            Input("segmentation-features", "value"),
            Input("sigma-range-slider", "value"),
        ],
        [
            State("masks", "data"),
        ],
    )
    def annotation_react(
        graph_relayoutData,
        any_label_class_button_value,
        stroke_width_value,
        show_segmentation_value,
        download_button_n_clicks,
        download_image_button_n_clicks,
        segmentation_features_value,
        sigma_range_slider_value,
        masks_data,
    ):
        classified_image_store_data = dash.no_update
        classifier_store_data = dash.no_update
        cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
        if cbcontext in ["segmentation-features.value", "sigma-range-slider.value"] or (
            ("Show segmentation" in show_segmentation_value)
            and (len(masks_data["shapes"]) > 0)
        ):
            segmentation_features_dict = {
                "intensity": False,
                "edges": False,
                "texture": False,
            }
            for feat in segmentation_features_value:
                segmentation_features_dict[feat] = True
            t1 = time()
            features = compute_features(
                img,
                **segmentation_features_dict,
                sigma_min=sigma_range_slider_value[0],
                sigma_max=sigma_range_slider_value[1],
            )
            t2 = time()
            print(t2 - t1)
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
            label_class_value = max(
                enumerate(any_label_class_button_value),
                key=lambda t: 0 if t[1] is None else t[1],
            )[0]

        fig = make_default_figure(
            stroke_color=class_to_color(label_class_value),
            stroke_width=stroke_width,
            shapes=masks_data["shapes"],
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
                segimgpng, clf = show_segmentation(
                    DEFAULT_IMAGE_PATH, masks_data["shapes"], features, feature_opts
                )
                if cbcontext == "download-button.n_clicks":
                    classifier_store_data = clf
                if cbcontext == "download-image-button.n_clicks":
                    classified_image_store_data = plot_common.pil_image_to_uri(
                        blend_image_and_classified_regions_pil(
                            PIL.Image.open(DEFAULT_IMAGE_PATH), segimgpng
                        )
                    )
            except ValueError:
                # if segmentation fails, draw nothing
                pass
            images_to_draw = []
            if segimgpng is not None:
                images_to_draw = [segimgpng]
            fig = plot_common.add_layout_images_to_fig(fig, images_to_draw)
        fig.update_layout(uirevision="segmentation")
        return (
            fig,
            masks_data,
            "Current paintbrush width: %d" % (stroke_width,),
            classifier_store_data,
            classified_image_store_data,
        )
