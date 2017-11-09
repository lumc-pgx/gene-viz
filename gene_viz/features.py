"""
Gene feature definitions
"""
class Feature(object):
    """
    Base class for all features
    """
    def __init__(self, feature_id="", children=None, start=0, end=0, strand="+"):
        self.id = feature_id
        self.children = children
        self.start = start
        self.end = end
        self.strand = strand


class Gene(Feature):
    """
    Feature representing a gene - a container of transcripts
    """
    def __init__(self, gene_id="", transcripts=[], start=0, end=0, strand="+"):
        super(Gene, self).__init__(gene_id, transcripts, start, end, strand)

    @property
    def gene_id(self):
        return self.id

    @gene_id.setter
    def gene_id(self, value):
        self.id = value

    @property
    def transcripts(self):
        return self.children

    @transcripts.setter
    def transcripts(self, value):
        self.children = value


class Transcript(Feature):
    """
    Feature representing a transcript - a container of exons
    """
    def __init__(self, transcript_id="", exons=[], start=0, end=0, strand="+", gene=None):
        super(Transcript, self).__init__(transcript_id, exons, start, end, strand)
        self.gene = gene

    @property
    def transcript_id(self):
        return self.id

    @transcript_id.setter
    def transcript_id(self, value):
        self.id = value

    @property
    def gene_id(self):
        return self.gene.gene_id

    @property
    def exons(self):
        return self.children


class Exon(Feature):
    """
    Feature representing an exon
    """
    def __init__(self, exon_id="", start=0, end=0, strand="+"):
        super(Exon, self).__init__(exon_id, None, start, end, strand)
        self.cds = None

    @property
    def exon_id(self):
        return self.id

    @exon_id.setter
    def exon_id(self, value):
        self.id = value