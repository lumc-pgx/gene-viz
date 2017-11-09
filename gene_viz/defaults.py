"""
defaults for visualization parameters
"""
from .colors import desaturate_named_color

exon_color_schemes = {
    "standard" : {
        "coding": "Gray",
        "noncoding": "DarkGrey",
        "monochrome_coding": "Black",
        "monochrome_noncoding": "Gray"
    },
    "reference" : {
        "coding": "MidnightBlue",
        "noncoding": desaturate_named_color("MidnightBlue", 0.4),
        "monochrome_coding": "Black",
        "monochrome_noncoding": "Gray"
    }
}

intron_color = "DarkGrey"
exon_base_color = "DarkGrey"
intron_marker_size = "7pt"
intron_marker_symbol = "v"
intron_marker_alpha = 0.75
intron_width_percent = 0.015
label_scale_factor = 0.006
gene_height = 0.8
coding_exon_height = 0.6
noncoding_exon_height = 0.3
coding_exon_halfheight = coding_exon_height / 2
noncoding_exon_halfheight = noncoding_exon_height / 2
left_pad_percent = 0.1
right_pad_percent = 0.02
axis_height = 35
row_height = 12
min_height = 50
exon_indicator_color = "tan"
exon_indicator_alpha = 0.6

# intron arrow direction
intron_marker_angle = {
    "-": -90,
    "+": 90
}

# valid options for axis location
axis_locations = ("above", "below")

# valid options for transcript label field
label_fields = ("id", "name")
