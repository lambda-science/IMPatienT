from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import os
from impatient.app.dashapp import bp
import impatient.app.dashapp.plot_common as plot_common
import impatient.app.dashapp.common_func as common_func
import json

DEFAULT_STROKE_WIDTH = 3  # gives line width of 2^3 = 8

onto_tree_imgannot = common_func.load_onto()
class_label_colormap = [
    i["data"]["hex_color"]
    for i in onto_tree_imgannot
    if i["data"]["image_annotation"] is True
]
class_labels = [
    i["text"] for i in onto_tree_imgannot if i["data"]["image_annotation"] is True
]
assert len(class_labels) <= len(class_label_colormap)  # nosec


def class_to_color(ontology, class_name):
    for term in ontology:
        if term["text"] == class_name:
            return term["data"]["hex_color"]


def get_external_stylesheets():
    external_stylesheets = [
        dbc.themes.BOOTSTRAP,
        os.path.join(bp.static_url_path, "segmentation-style.css"),
    ]
    return external_stylesheets


# Modal
with open(os.path.join(bp.static_folder, "explanations.md"), "r") as f:
    howto_md = f.read()

# Header
header = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H3("Image Annotation Module"),
                                ],
                                id="app-title",
                            )
                        ],
                        align="center",
                    ),
                    dbc.Col(
                        dbc.Nav(
                            [
                                html.Div(
                                    [
                                        html.A(
                                            "Return To Index",
                                            href="/img_index",
                                        ),
                                    ]
                                )
                            ]
                        )
                    ),
                ],
                align="center",
            ),
        ],
        fluid=True,
    ),
    dark=True,
    color="dark",
    sticky="top",
)
# Description
description = dbc.Col(
    [
        dbc.Card(
            id="description-card",
            children=[
                dbc.CardHeader("Explanation"),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.B(
                                            "If your image is not displayed please hit F5 to refresh the page, it should solve most issues."
                                        ),
                                        html.P(
                                            "This is the image annotation tool interface. "
                                            "Select the standard vocabulary term and draw on the image to annotate parts of the image. "
                                            "Then check the 'Compute Segmentation' tickbox to automatically expands your annotations to the whole image. "
                                            "You may add more marks to clarify parts of the image where the classifier was not successful",
                                            "and the classification will update. Once satisfied with the annotations area you can click the"
                                            "'Save Annotation To Database' to save your annotations.",
                                        ),
                                    ],
                                    md=True,
                                ),
                            ]
                        ),
                    ]
                ),
            ],
        )
    ],
    md=12,
)
# Image Segmentation
segmentation = [
    html.Div([dcc.Location(id="url")]),
    dbc.Card(
        id="segmentation-card",
        children=[
            dbc.CardHeader("Image Viewer"),
            dbc.CardBody(
                [
                    # Wrap dcc.Loading in a div to force transparency when loading
                    html.Div(
                        id="transparent-loader-wrapper",
                        children=[
                            dcc.Loading(
                                id="segmentations-loading",
                                type="circle",
                                children=[
                                    # Graph
                                    dcc.Graph(
                                        id="graph",
                                        figure=plot_common.dummy_fig(),
                                        config={
                                            "scrollZoom": True,
                                            "modeBarButtonsToAdd": [
                                                "drawopenpath",
                                                "eraseshape",
                                            ],
                                        },
                                    ),
                                ],
                            )
                        ],
                    ),
                ]
            ),
            dbc.CardFooter(
                [
                    # Download links
                    html.A(
                        id="download",
                        download="classifier.json",
                    ),
                    html.Div(
                        children=[
                            html.Div(id="alertbox"),
                            dbc.ButtonGroup(
                                [
                                    dbc.Button(
                                        "Save Segmentation to Database",
                                        id="download-button",
                                        color="success",
                                    )
                                ],
                                size="lg",
                                style={"width": "100%"},
                            ),
                        ],
                    ),
                    html.A(
                        id="download-image",
                        download="classified-image.png",
                    ),
                ]
            ),
        ],
    ),
]

# sidebar
sidebar = [
    dbc.Card(
        id="sidebar-card",
        children=[
            dbc.CardHeader("Tool-Box"),
            dbc.CardBody(
                [
                    html.H6("Standard Vocabulary Term", className="card-title"),
                    # Label class chosen with buttons
                    html.Div(
                        id="label-class-buttons",
                        children=[
                            dbc.Button(
                                c,
                                id={"type": "label-class-button", "index": n},
                                style={
                                    "background-color": class_to_color(
                                        onto_tree_imgannot, c
                                    )
                                },
                            )
                            for n, c in enumerate(class_labels)
                        ],
                    ),
                    html.Hr(),
                    dbc.Form(
                        [
                            dbc.Row(
                                [
                                    dbc.Label(
                                        "Paintbrush Size",
                                        html_for="stroke-width",
                                    ),
                                    # Slider for specifying stroke width
                                    dcc.Slider(
                                        id="stroke-width",
                                        min=0,
                                        max=6,
                                        step=0.1,
                                        marks=None,
                                        value=DEFAULT_STROKE_WIDTH,
                                    ),
                                ]
                            ),
                            dbc.Row(
                                [
                                    dbc.Label(
                                        "Segmentation stringency range",
                                        html_for="sigma-range-slider",
                                    ),
                                    dcc.RangeSlider(
                                        id="sigma-range-slider",
                                        min=0.01,
                                        max=20,
                                        step=0.01,
                                        marks=None,
                                        value=[0.5, 4],
                                    ),
                                ]
                            ),
                            # Indicate showing most recently computed segmentation
                            dcc.Checklist(
                                id="show-segmentation",
                                options=[
                                    {
                                        "label": "COMPUTE SEGMENTATION",
                                        "value": "Show segmentation",
                                    }
                                ],
                                style={
                                    "border": "solid",
                                    "color": "red",
                                    "border-radius": "30px",
                                    "text-align": "center",
                                },
                                value=[],
                            ),
                        ]
                    ),
                ]
            ),
        ],
    ),
]

meta = [
    html.Div(
        id="no-display",
        children=[
            # Store for user created masks
            # data is a list of dicts describing shapes
            dcc.Store(id="masks", data={"shapes": []}),
            dcc.Store(id="classifier-store", data={}),
            dcc.Store(id="classified-image-store", data=""),
            dcc.Store(id="features_hash", data=""),
        ],
    ),
    html.Div(id="download-dummy"),
    html.Div(id="download-image-dummy"),
]

layout = html.Div(
    [
        header,
        dbc.Container(
            [
                dbc.Row(description),
                dbc.Row(
                    id="app-content",
                    children=[dbc.Col(segmentation, lg=8), dbc.Col(sidebar, lg=4)],
                ),
                dbc.Row(dbc.Col(meta)),
            ],
            fluid=True,
        ),
    ]
)
