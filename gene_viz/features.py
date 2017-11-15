"""
feature definitions
"""
from interval import interval


class Feature(object):
    """
    Base class for all features
    """
    def __init__(self, contig="", start=0, end=0):
        self.contig = contig
        self.extents = interval[start, end]

    @property
    def start(self):
        return int(self.extents[0][0])

    @start.setter
    def start(self, value):
        self.extents = interval[value, self.end]

    @property
    def end(self):
        return int(self.extents[0][1])

    @end.setter
    def end(self, value):
        self.extents = interval[self.start, value]

    @property
    def size(self):
        return self.end - self.start



class Transcript(Feature):
    """
    Feature representing a transcript
    """
    def __init__(self, transcript_id="", gene_id="", contig="", start=0, end=0, strand="+", exons=None, cds=None):
        super(Transcript, self).__init__(contig, start, end)
        self.transcript_id = transcript_id
        self.gene_id = gene_id
        self.exons = [] if exons is None else exons
        self.cds = [] if cds is None else cds
        self.strand = strand

    def add_exon(self, exon):
        self.exons.append(exon)

    def add_cds(self, cds):
        self.cds.append(cds)


class Exon(Feature):
    """
    Feature representing an exon
    """
    def __init__(self, exon_id="", contig="", start=0, end=0):
        super(Exon, self).__init__(contig, start, end)
        self.exon_id = exon_id


class CDS(Feature):
    """
    Feature representing a coding region
    """
    def __init__(self, contig="", start=0, end=0):
        super(CDS, self).__init__(contig, start, end)