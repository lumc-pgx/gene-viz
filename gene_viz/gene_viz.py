"""
Gene and transcript visualization
"""

# bokeh
from bokeh.models import (
    ColumnDataSource as CDS,
    Range1d,
    AdaptiveTicker,
    CompositeTicker,
    NumeralTickFormatter,
)

from bokeh.plotting import figure, Figure

# dataframe utilities
from .dataframes import (
    transcript_data_frame,
    transcript_label_data_frame,
    exon_data_frame,
    intron_data_frame,
    append_data,
    concat_data,
)

from interval import interval

# defaults
from .defaults import defaults

# valid options for axis location
axis_locations = ("above", "below")


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
    def __init__(self, prefs={}):

        # dictionary to hold the dataframes to be rendered
        self._gene_data = dict(
            transcripts=CDS(self._placeholder()),
            coding_exons=CDS(exon_data_frame()),
            noncoding_exons=CDS(exon_data_frame()),
            introns=CDS(intron_data_frame()),
            labels=CDS(transcript_label_data_frame())
        )

        # preferences
        self._prefs = defaults
        self._prefs.update(prefs)

        # the transcript data from the database
        self._transcripts = None

        # flag to indicate if the gene data to display has changed
        self._dirty_flag = False

        # create the plot
        self._figure = self._create_plot()


    @staticmethod
    def _placeholder():
        temp_data = transcript_data_frame(1)
        temp_data.iloc[0] = [0, 0, 0, 0]
        return temp_data


    def _create_plot(self):
        fig = figure(width=800, height=100, tools=["xpan, xwheel_zoom, xbox_zoom, save, reset"],
                     active_scroll="xwheel_zoom",
                     toolbar_location=None, logo=None, x_axis_location=self.prefs["axis_location"],
                     x_range = (0,1), y_range=(-1, 1))

        # transcript center line
        fig.segment(x0="x0", y0="y0", x1="x1", y1="y1", color=self.prefs["intron_line_color"],
                    source=self._gene_data["transcripts"], name="transcripts")

        # intron markers
        fig.text(x="x", y="y", text=dict(value=self.prefs["intron_marker_symbol"]), angle="angle", angle_units="deg",
                 text_align="center", text_baseline="middle", text_font="sans-serif", text_color=self.prefs["intron_marker_color"],
                 text_font_style="bold", text_alpha="alpha", text_font_size=self.prefs["intron_marker_size"],
                 source=self._gene_data["introns"], name="introns")

        # coding exons
        fig.quad(left="x0", bottom="y0", right="x1", top="y1", color=self.prefs["exon_color"],
                 source=self._gene_data["coding_exons"], name="coding_exons")

        # non-coding exons
        fig.quad(left="x0", bottom="y0", right="x1", top="y1", color=self.prefs["exon_color"],
                 source=self._gene_data["noncoding_exons"], name="noncoding_exons")

        # transcript labels
        fig.text(x="x1", y="mid", text="label", text_font_size=self.prefs["label_font_size"], text_align="right", text_baseline="middle",
                 source=self._gene_data["labels"], text_font=self.prefs["label_font"], name="transcript_labels")


        fig.yaxis.visible = False
        fig.xaxis.ticker = transcript_track_ticker()
        fig.xaxis.formatter = NumeralTickFormatter(format="0,0")
        fig.xgrid.grid_line_color = None
        fig.ygrid.grid_line_color = None
        fig.outline_line_alpha = 0

        return fig


    def _get_label_data(self, transcript):
        """
        Create a dataframe for the label of a transcript

        :param transcript: A pyensembl transcript object
        :param y: The y-axis position

        :return: A transcript_label_data_frame for the current transcript
        """
        id_data = transcript_label_data_frame(1)
        transcript_id = transcript.transcript_id
        length = self.prefs["label_scale_factor"] * (len(transcript_id) + 1) * (self.x_range.end - self.x_range.start)
        y = transcript.draw_level

        id_data.loc[0] = [transcript.start - length - 1, y - self.prefs["transcript_height"] / 2,
                          transcript.start - 1, y + self.prefs["transcript_height"] / 2, y, "{} ".format(transcript_id)]

        return id_data


    def _get_transcript_bounds_data(self, transcript):
        """
        Create a dataframe containing the bounds of a transcript

        :param transcript: A pyensembl transcript object
        :param y: The y-axis position

        :return: A gene_data_frame for the current transcript
        """
        transcript_data = transcript_data_frame(1)
        y = transcript.draw_level
        transcript_data.loc[0] = [transcript.start - 1, y, transcript.end, y]
        return transcript_data


    def _get_exon_data(self, transcript):
        """
        Create dataframes for exon blocks

        :param transcript: The pyensembl transcript object to be drawn
        :param y: The y-axis position of the track

        :return: An pair of exon dataframes, one containing exons for a coding transcript,
                 the other containing exons for a non-coding transcript
        """
        exons = transcript.exons
        cds = transcript.cds

        coding_exon_half_height = self.prefs["coding_exon_height"] / 2
        noncoding_exon_half_height = self.prefs["noncoding_exon_height"] / 2

        y = transcript.draw_level
        exon_data = exon_data_frame(len(exons))
        for i, exon in enumerate(exons):
            exon_data.loc[i] = [exon.start - 1, y - noncoding_exon_half_height, exon.end, y + noncoding_exon_half_height]

        cds_data = exon_data_frame(len(cds))
        for i, c in enumerate(cds):
            cds_data.loc[i] = [c.start - 1, y - coding_exon_half_height, c.end, y + coding_exon_half_height]

        return cds_data, exon_data


    def _get_intron_data(self, transcript):
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

        intron_width = self.prefs["intron_width_percent"] * (self.x_range.end - self.x_range.start)

        y = transcript.draw_level

        for exon in exons:
            if exon is not exons[-1]:
                next_exon = exons[exons.index(exon) + 1]
                width = next_exon.start - exon.end
                mid = exon.end + width / 2
                intron_data.loc[len(intron_data)] = [mid, y, self.prefs["intron_marker_angle"][transcript.strand], width,
                                                     self.prefs["intron_marker_alpha"] if width > intron_width else 0]

        return intron_data


    def update(self, callback_fn=None):
        #print("update gene plot, dirty={}".format(self._dirty_flag))
        if self._transcripts is None:
            return

        self.pack(self._transcripts)

        num_levels = max([t.draw_level for t in self._transcripts]) + 1
        self._figure.plot_height = max(self.prefs["min_height"], self.prefs["row_height"] * (num_levels + 1) + self.prefs["axis_height"])
        self._figure.y_range.start, self._figure.y_range.end = (num_levels, -1)

        transcript_data = []
        exon_data_coding = []
        exon_data_noncoding = []
        intron_data = []
        label_data = []

        for transcript in self._transcripts:
            if self._dirty_flag:
                # center line from transcript start to transcript end
                append_data(
                    self._get_transcript_bounds_data(transcript),
                    transcript_data
                )

                # labels
                append_data(
                    self._get_label_data(transcript),
                    label_data
                )

                # exons
                exons_coding, exons_noncoding = self._get_exon_data(transcript)
                append_data(
                    exons_coding, exon_data_coding
                )

                append_data(
                    exons_noncoding, exon_data_noncoding
                )

                # introns / strand direction markers
                append_data(
                    self._get_intron_data(transcript),
                    intron_data
                )
            else:
                pass


        # update graph sources with new data
        if self._dirty_flag:
            self._gene_data["transcripts"].data = CDS.from_df(concat_data(transcript_data, transcript_data_frame))
            self._gene_data["coding_exons"].data = CDS.from_df(concat_data(exon_data_coding, exon_data_frame))
            self._gene_data["noncoding_exons"].data = CDS.from_df(concat_data(exon_data_noncoding, exon_data_frame))
            self._gene_data["introns"].data = CDS.from_df(concat_data(intron_data, intron_data_frame))
            if self.prefs["show_labels"]:
                self._gene_data["labels"].data = CDS.from_df(concat_data(label_data, transcript_label_data_frame))
        else:
            pass
            
        # everything up-to-date
        self._dirty_flag = False

        if callback_fn is not None:
            callback_fn()


    def pack(self, transcripts):
        if self.prefs.get("pack", False):
            sorted_t = sorted(transcripts, key=lambda x: (x.gene_id, x.size, x.start))
            packed_t = [sorted_t[0]]
            packed_t[-1].draw_level = 0

            for t1 in sorted_t[1:]:
                t1.draw_level = 0
                for t2 in packed_t:
                    if len(t1.extents & t2.extents) > 0:
                        if t2.draw_level >= t1.draw_level:
                            t1.draw_level = t2.draw_level + 1

                packed_t.append(t1)
        else:
            for i, t in enumerate(transcripts):
                t.draw_level = i



    def link_x_range(self, other):
        """
        Link the x-axis of this figure to the x-axis of other

        :param other: a bokeh Figure
        """
        assert isinstance(other, Figure), "Error - other must be a bokeh figure object"
        self.figure.x_range = other.x_range


    @property
    def transcripts(self):
        return self._transcripts


    @transcripts.setter
    def transcripts(self, value):
        self._transcripts = value
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

        self._figure.x_range.start = start
        self._figure.x_range.end = end
        self.figure.x_range.bounds = bounds

    @property
    def prefs(self):
        return self._prefs
