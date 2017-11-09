"""
Gene and transcript visualization
"""

# bokeh
from bokeh.models import (
    ColumnDataSource as CDS,
    Quad,
    HoverTool,
    TapTool,
    LassoSelectTool,
    CustomJS,
    Range1d,
    LinearAxis,
    AdaptiveTicker,
    CompositeTicker,
    NumeralTickFormatter,
    Div,
)

from bokeh.plotting import figure, Figure

# dataframe utilities
from .dataframes import (
    gene_data_frame,
    gene_id_data_frame,
    exon_data_frame,
    intron_data_frame,
    append_data,
    concat_data,
)

# color generation
from . import colors

# defaults
from . import defaults


def transcript_track_ticker():
    """
    Create a composite ticker so that sensible axis values and tick intervals are used at all zoom levels
    :return: A bokeh composite ticker
    """
    return CompositeTicker(
        tickers=[
            AdaptiveTicker(base=10, mantissas=list(range(1, 10)), min_interval=1, max_interval=1, num_minor_ticks=1),
            AdaptiveTicker(base=10, mantissas=list(range(1, 10)), min_interval=2, max_interval=2, num_minor_ticks=2),
            AdaptiveTicker(base=10, mantissas=list(range(1, 10)), min_interval=3, max_interval=3, num_minor_ticks=3),
            AdaptiveTicker(base=10, mantissas=list(range(1, 10)), min_interval=4, max_interval=4, num_minor_ticks=4),
            AdaptiveTicker(base=10, mantissas=list(range(1, 10)), min_interval=5, num_minor_ticks=5)
        ]
    )


class GenePlot(object):
    def __init__(self,
                 axis_location="above",
                 id_label="id",
                 color_scheme=defaults.exon_color_schemes["standard"]):

        # dictionary to hold the dataframes to be rendered
        self._gene_data = dict(
            center=CDS(self._gene_placeholder()),
            coding_transcript_exons=CDS(exon_data_frame()),
            noncoding_transcript_exons=CDS(exon_data_frame()),
            introns=CDS(intron_data_frame()),
            labels=CDS(gene_id_data_frame())
        )

        # x_axis position
        assert axis_location in defaults.axis_locations, "Invalid axis location '{}', must be one of '{}'".format(axis_location, ", ".join(defaults.axis_locations))
        self._x_axis_location = axis_location

        # transcript label fields
        assert id_label in defaults.label_fields, "Invalid id_label '{}', must be one of '{}'".format(id_label, ", ".join(defaults.label_fields))
        self._id_label = id_label

        # the gene data from the database
        self._genes = None

        # base color scheme
        self._exon_color_scheme = color_scheme

        # differentiate between coding and non-coding regions?
        self._show_coding = True

        # flag to indicate if the gene data to display has changed
        self._dirty_flag = False

        # create the plot
        self._figure = self._create_plot()


    @staticmethod
    def _gene_placeholder():
        temp_data = gene_data_frame(1)
        temp_data.iloc[0] = [0, 0, 0, 0]
        return temp_data


    def _create_plot(self):
        fig = figure(width=800, height=100, tools=["xpan, xwheel_zoom, xbox_zoom, save, reset"],
                     active_scroll="xwheel_zoom",
                     toolbar_location=None, logo=None, x_axis_location=self._x_axis_location,
                     x_range = (0,1), y_range=(-1, 1))

        # transcript center line
        fig.segment(x0="x0", y0="y0", x1="x1", y1="y1", color=defaults.intron_color, alpha=0.75, line_width=1,
                    source=self._gene_data["center"], name="center_lines")

        # intron markers
        fig.text(x="x", y="y", text=dict(value=defaults.intron_marker_symbol), angle="angle", angle_units="deg",
                 text_align="center", text_baseline="middle", text_font="sans-serif", text_color=defaults.intron_color,
                 text_font_style="bold", text_alpha="alpha", text_font_size=defaults.intron_marker_size,
                 source=self._gene_data["introns"], name="introns")

        # exons for coding transcripts
        coding_transcript_exons = Quad(left="x0", right="x1", bottom="y0", top="y1",
                     line_color=self._exon_color_scheme["coding"], fill_color=self._exon_color_scheme["coding"],
                     line_width=1)
        fig.add_glyph(self._gene_data["coding_transcript_exons"], coding_transcript_exons,
                      selection_glyph=coding_transcript_exons, nonselection_glyph=coding_transcript_exons,
                      name="coding_transcript_exons")

        # exons for non-coding transcripts
        noncoding_transcript_exons = Quad(left="x0", right="x1", bottom="y0", top="y1",
                                       line_color=self._exon_color_scheme["noncoding"],
                                       fill_color=self._exon_color_scheme["noncoding"],
                                       line_width=1)
        fig.add_glyph(self._gene_data["noncoding_transcript_exons"], noncoding_transcript_exons,
                      selection_glyph=noncoding_transcript_exons, nonselection_glyph=noncoding_transcript_exons,
                      name="noncoding_transcript_exons")

        # transcript names
        fig.text(x="x1", y="mid", text="transcript_id", text_font_size="7pt", text_align="right", text_baseline="middle",
                 source=self._gene_data["labels"], text_font="monospace", name="transcript_ids")

        # invisible boxes around transcript names for selecting
#        tags = Quad(left="x0", right="x1", bottom="y0", top="y1",
#                    fill_color="white", line_color="black", fill_alpha=0, line_alpha=0, line_width=1)
#        fig.add_glyph(self._gene_data["labels"], tags, selection_glyph=tags,
#                      nonselection_glyph=tags, name="tags")

        fig.yaxis.visible = False
        fig.xaxis.ticker = transcript_track_ticker()
        fig.xaxis.formatter = NumeralTickFormatter(format="0,0")
        fig.xgrid.grid_line_color = None
        fig.ygrid.grid_line_color = None
        fig.outline_line_alpha = 0

#        fig.add_tools(
#            TapTool(
#                renderers=fig.select(name="coding_transcript_exons") + fig.select(name="noncoding_transcript_exons") \
#                          + fig.select(name="tags")
#            )
#        )

#        if self._tooltips:
#            fig.add_tools(
#                HoverTool(
#                    tooltips=label_tooltips, point_policy="snap_to_data", attachment="vertical",
#                    renderers=fig.select(name="tags")
#                )
#            )

        return fig

    #def add_x_range_callback(self, intron_sources, label_sources, locus_div):
        #"""
        #Add a client side callback to react to changes in the x-axis range

        #:param intron_sources: A list of column data sources containing the intron data to operate on
        #:param label_sources: A list of column data sources containing gene_id labels
        #:param locus_div: The div to update with the currently displayed coordinates
        #"""
        #assert isinstance(intron_sources, list) and all(isinstance(s, CDS) for s in intron_sources), \
            #"Error - intron_sources must be a list of ColumnDataSources"

        #assert isinstance(label_sources, list) and all(isinstance(s, CDS) for s in label_sources), \
            #"Error - label_sources must be a list of ColumnDataSources"

        #assert isinstance(locus_div, Div), "Error - locus_div must be a Div object"

        #try:
            #callback_filename = "java_script/gene_range_callback.js"
            #callback_code = open(callback_filename, "r").read() % (intron_width_percent, intron_marker_alpha, label_scale_factor)
        #except IOError:
            #print("Unable to load callback code from file '{}'".format(callback_filename))
            #return

        #cb_args = dict()
        #for i in range(len(intron_sources)):
            #cb_args["intron_data_{}".format(i)] = intron_sources[i]

        #for i in range(len(label_sources)):
            #cb_args["label_data_{}".format(i)] = label_sources[i]

        #cb_args["locus_div"] = locus_div

        #self._figure.x_range.callback = CustomJS(
            #args=cb_args,
            #code=callback_code
        #)


    def _exon_color_mapping(self):
        """
        override this to create a dictionary which maps from exon
        coordinates to exon color
        """
        return dict()
        
        
    def _get_gene_id_data(self, transcript, y):
        """
        Create a dataframe for the gene_id label of a transcript

        :param transcript: A pyensembl transcript object
        :param y: The y-axis position

        :return: A gene_id_data_frame for the current transcript
        """
        label_field = self._id_label
        id_data = gene_id_data_frame(1)
        transcript_id = transcript.id if label_field == "id" else transcript.name
        gene_id = transcript.gene.id if label_field == "id" else transcript.gene.name
        length = defaults.label_scale_factor * (len(transcript_id) + 1) * (self.x_range.end - self.x_range.start)
        id_data.loc[0] = [transcript.start - length - 1, y - defaults.gene_height / 2,
                          transcript.start - 1, y + defaults.gene_height / 2, y,
                          gene_id, "{} ".format(transcript_id)]
        return id_data


    def _get_transcript_bounds_data(self, transcript, y):
        """
        Create a dataframe containing the bounds of a transcript

        :param transcript: A pyensembl transcript object
        :param y: The y-axis position

        :return: A gene_data_frame for the current transcript
        """
        transcript_data = gene_data_frame(1)
        transcript_data.loc[0] = [transcript.start - 1, y, transcript.end, y]
        return transcript_data


    def _get_exon_data(self, transcript, y, mapper):
        """
        Create dataframes for exon blocks

        :param transcript: The pyensembl transcript object to be drawn
        :param y: The y-axis position of the track

        :return: An pair of exon dataframes, one containing exons for a coding transcript,
                 the other containing exons for a non-coding transcript
        """
        exons = transcript.exons

        has_coding = self._show_coding and any(True for x in transcript.exons if x.cds is not None)

        is_coding = not self._show_coding or has_coding
        exon_data_coding = exon_data_frame(len(exons) if is_coding else 0)
        exon_data_noncoding = exon_data_frame(len(exons) if not is_coding else 0)
        exon_data = exon_data_coding if is_coding else exon_data_noncoding

        coding_exon_halfheight = defaults.coding_exon_halfheight
        noncoding_exon_halfheight = defaults.noncoding_exon_halfheight if self._show_coding else coding_exon_halfheight

        cur_row = 0
        # process each exon
        for exon in exons:
            if not has_coding and self._show_coding:
                color = self._exon_color_scheme["noncoding"]
            else:
                color = self._exon_color_scheme["coding"]

#            if transcript.gene_id == self._focus:
#                try:
#                    color = mapper[(exon.start - 1, exon.end)]
#                    if not has_coding and self._show_coding:
#                        color = colors.desaturate_hex(color, 0.4)
#                except KeyError:
#                    pass

            # find the CDS for this exon
            cds = exon.cds
            has_noncoding = cds is None or exon.start < cds.start or exon.end > cds.end

            # draw non-coding portion
            if has_noncoding:
                exon_data.loc[cur_row] = [exon.start - 1, y - noncoding_exon_halfheight,
                                          exon.end, y + noncoding_exon_halfheight, color]
                cur_row += 1

            # then coding portion
            if cds is not None:
                exon_data.loc[cur_row] = [cds.start - 1, y - coding_exon_halfheight,
                                          cds.end, y + coding_exon_halfheight, color]
                cur_row += 1

        return exon_data_coding, exon_data_noncoding


    def _get_intron_data(self, transcript, y):
        """
        Create a dataframe for a track of introns / strand markers
        :param transcript: The pyensembl transcript object to be drawn
        :param y: the y-axis position of the track

        :return: an intron_data_frame for the introns of transcript
        """
        intron_data = intron_data_frame()

        exons = sorted(transcript.exons, key=lambda x: x.start)
        if len(exons) < 2:
            return intron_data

        intron_width = defaults.intron_width_percent * (self.x_range.end - self.x_range.start)

        for exon in exons:
            if exon is not exons[-1]:
                next_exon = exons[exons.index(exon) + 1]
                width = next_exon.start - exon.end
                mid = exon.end + width / 2
                intron_data.loc[len(intron_data)] = [mid, y, defaults.intron_marker_angle[transcript.strand], width,
                                                     defaults.intron_marker_alpha if width > intron_width else 0]

        return intron_data


    def update(self, callback_fn=None):
        #print("update gene plot, dirty={}".format(self._dirty_flag))
        if self._genes is None:
            return

        num_transcripts = sum(1 for gene in self._genes for transcript in gene.transcripts)
        self._figure.plot_height = max(defaults.min_height, defaults.row_height * (num_transcripts + 1) + defaults.axis_height)
        self._figure.y_range.start, self._figure.y_range.end = (num_transcripts, -1)

        color_mapper = self._exon_color_mapping()

        transcript_data = []
        exon_data_coding = []
        exon_data_noncoding = []
        intron_data = []
        label_data = []
        counter = 0

        for gene in self._genes:
            for transcript in gene.transcripts:
                if self._dirty_flag:
                    # center line from transcript start to transcript end
                    append_data(
                        self._get_transcript_bounds_data(transcript, y=counter),
                        transcript_data
                    )

                    # labels
                    append_data(
                        self._get_gene_id_data(transcript, y=counter),
                        label_data
                    )

                    # exons
                    exons_coding, exons_noncoding = self._get_exon_data(transcript, y=counter, mapper=color_mapper)
                    append_data(
                        exons_coding, exon_data_coding
                    )

                    append_data(
                        exons_noncoding, exon_data_noncoding
                    )

                    # introns / strand direction markers
                    append_data(
                        self._get_intron_data(transcript, y=counter),
                        intron_data
                    )
                else:
                    pass

                counter += 1

        # update graph sources with new data
        if self._dirty_flag:
            self._gene_data["center"].data = CDS.from_df(concat_data(transcript_data, gene_data_frame))
            self._gene_data["coding_transcript_exons"].data = CDS.from_df(concat_data(exon_data_coding, exon_data_frame))
            self._gene_data["noncoding_transcript_exons"].data = CDS.from_df(concat_data(exon_data_noncoding, exon_data_frame))
            self._gene_data["introns"].data = CDS.from_df(concat_data(intron_data, intron_data_frame))
            self._gene_data["labels"].data = CDS.from_df(concat_data(label_data, gene_id_data_frame))
        else:
            pass
            
        # everything up-to-date
        self._dirty_flag = False

        if callback_fn is not None:
            callback_fn()


    def link_x_range(self, other):
        """
        Link the x-axis of this figure to the x-axis of other

        :param other: a bokeh Figure
        """
        assert isinstance(other, Figure), "Error - other must be a bokeh figure object"
        self.figure.x_range = other.x_range


    @staticmethod
    def pad_x_range(range):
        """
        Pad the start and end of range

        :param range: the Range1d object to be padded
        :return: a Range1d containing the padded range
        """
        assert isinstance(range, Range1d), "Error - range must be a Range1d object"
        start, end = (range.start, range.end)
        width = end - start
        left_pad, right_pad = (defaults.left_pad_percent * width, defaults.right_pad_percent * width)

        padded_range = Range1d(
            start = start - left_pad,
            end = end + right_pad
        )

        if range.bounds is not None:
            bounds = (range.bounds[0], range.bounds[1])
            if padded_range.start < bounds[0]:
                bounds = (padded_range.start, bounds[1])
            if padded_range.end > bounds[1]:
                bounds = (bounds[0], padded_range.end)
            padded_range.bounds = bounds

        return padded_range


    @property
    def genes(self):
        return self._genes


    @genes.setter
    def genes(self, value):
        self._genes = value
        self._dirty_flag = True


    @property
    def figure(self):
        return self._figure


    @property
    def x_range(self):
        return self._figure.x_range


    @x_range.setter
    def x_range(self, value):
        if isinstance(value, Range1d):
            start, end = (value.start, value.end)
            bounds = value.bounds
        elif isinstance(value, tuple) and len(value) == 2:
            start, end = (value[0], value[1])
            bounds = None
        else:
            print("Error - value must be either a bokeh Range1D or a two element tuple containing start and end values")
            raise ValueError

        #if bounds is None:
        #    bounds = (start, end)

        self._figure.x_range.start = start
        self._figure.x_range.end = end
        self.figure.x_range.bounds = bounds


    @property
    def exon_data(self):
        return [self._gene_data["coding_transcript_exons"], self._gene_data["noncoding_transcript_exons"]]


    @property
    def intron_data(self):
        return self._gene_data["introns"]


    @property
    def label_data(self):
        return self._gene_data["labels"]


    @property
    def show_coding(self):
        return self._show_coding


    @show_coding.setter
    def show_coding(self, value):
        assert isinstance(value, bool), "Error - show_coding must be True or False, not {}".format(value)
        self._show_coding = value
        self._dirty_flag = True
