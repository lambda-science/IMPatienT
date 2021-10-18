from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import os
from app.dashapp import bp
import app.dashapp.plot_common as plot_common

DEFAULT_STROKE_WIDTH = 3  # gives line width of 2^3 = 8

SEG_FEATURE_TYPES = ["intensity", "edges", "texture"]

class_label_colormap = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2"]
class_labels = ["Rods", "Core", "Cytoplasme", "Noyaux", "Autre"]
assert len(class_labels) <= len(class_label_colormap)


def class_to_color(n):
    return class_label_colormap[n]


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
                                    html.P(
                                        "This is the image annotation tool interface. "
                                        "Select the label and draw on the image to annotate parts of the image. "
                                        'Then check the "Show Segmentation" tickbox to automatically expands your annotations to the whole image. '
                                        "You may add more marks to clarify parts of the image where the classifier was not successful and the classification"
                                        "classifier was not successful and the classification will update. Once satisfied with the annotations area you can click the"
                                        '"Save Annotation To Database" to save your annotations.'
                                    ),
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
            dbc.CardHeader("Viewer"),
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
                                        "Save Annotation to Database",
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
            dbc.CardHeader("Tools"),
            dbc.CardBody(
                [
                    html.H6("Label class", className="card-title"),
                    # Label class chosen with buttons
                    html.Div(
                        id="label-class-buttons",
                        children=[
                            dbc.Button(
                                c,
                                id={"type": "label-class-button", "index": n},
                                style={"background-color": class_to_color(n)},
                            )
                            for n, c in enumerate(class_labels)
                        ],
                    ),
                    html.Hr(),
                    dbc.Form(
                        [
                            dbc.FormGroup(
                                [
                                    dbc.Label(
                                        "Width of annotation paintbrush",
                                        html_for="stroke-width",
                                    ),
                                    # Slider for specifying stroke width
                                    dcc.Slider(
                                        id="stroke-width",
                                        min=0,
                                        max=6,
                                        step=0.1,
                                        value=DEFAULT_STROKE_WIDTH,
                                    ),
                                ]
                            ),
                            dbc.FormGroup(
                                [
                                    html.H6(
                                        id="stroke-width-display",
                                        className="card-title",
                                    ),
                                    dbc.Label(
                                        "Blurring parameter",
                                        html_for="sigma-range-slider",
                                    ),
                                    dcc.RangeSlider(
                                        id="sigma-range-slider",
                                        min=0.01,
                                        max=20,
                                        step=0.01,
                                        value=[0.5, 4],
                                    ),
                                ]
                            ),
                            dbc.FormGroup(
                                [
                                    dbc.Label(
                                        "Select features",
                                        html_for="segmentation-features",
                                    ),
                                    dcc.Checklist(
                                        id="segmentation-features",
                                        options=[
                                            {"label": l.capitalize(), "value": l}
                                            for l in SEG_FEATURE_TYPES
                                        ],
                                        value=["intensity", "edges"],
                                    ),
                                ]
                            ),
                            # Indicate showing most recently computed segmentation
                            dcc.Checklist(
                                id="show-segmentation",
                                options=[
                                    {
                                        "label": "Show segmentation",
                                        "value": "Show segmentation",
                                    }
                                ],
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
                    children=[dbc.Col(segmentation, md=8), dbc.Col(sidebar, md=4)],
                ),
                dbc.Row(dbc.Col(meta)),
            ],
            fluid=True,
        ),
    ]
)
