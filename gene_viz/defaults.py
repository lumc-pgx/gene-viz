"""
defaults for visualization parameters
"""

defaults = dict(
    axis_location = "below",
    axis_height=35,
    row_height=12,
    min_height=50,

    exon_color = "DarkBlue",
    coding_exon_height = 0.7,
    noncoding_exon_height = 0.35,

    intron_line_color = "Black",
    intron_marker_color = "Black",
    intron_marker_size = "5pt",
    intron_marker_symbol = "v",
    intron_marker_alpha = 1,
    intron_width_percent = 0.015,

    # intron arrow direction
    intron_marker_angle={
        "-": -90,
        "+": 90
    },

    show_labels = True,
    label_horiz_position = "left",
    label_vert_position = "above",
    label_justify = "left",
    label_offset = (0, 0),
    label_scale_factor = 0.006,
    label_font="monospace",
    label_font_size = "7pt",

    pack = False,
)
