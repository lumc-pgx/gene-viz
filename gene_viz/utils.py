"""
Utilities and helpers
"""

import sys
from .features import Transcript, Exon, CDS


def transcripts_from_gffutils(db, contig, start, end):
    """
    Utility function to create gene_viz transcript objects from a gffutils database

    :param db:      Connection to a gffutils database
    :param contig:  Name of contig to use in query
    :param start:   Start position of query
    :param end:     End position of query
    :return:        A list of gene_viz transcript objects

    example usage
    >>> from gene_viz.utils import transcripts_from_gffutils
    >>> db = gffutils.FeatureDB("path/to/dbfile")
    >>> transcripts = transcripts_from_gffutils(db, "chr2", 2210223, 2300331)
    """
    transcript_list = []

    try:
        import gffutils
        always_return_list = gffutils.constants.always_return_list
    except ImportError:
        print("Unable to import gff_utils", file=sys.stderr)
        raise

    gffutils.constants.always_return_list = False

    for gene in db.features_of_type("gene", limit=(contig, start, end)):
        transcripts = db.children(gene.id, featuretype="transcript")
        for transcript in transcripts:
            t = Transcript(transcript.attributes["transcript_name"], gene.attributes["gene_name"],
                           transcript.seqid, transcript.start, transcript.end, transcript.strand)

            exons = db.children(transcript.id, featuretype="exon")
            for exon in exons:
                t.add_exon(Exon(exon.attributes["exon_id"], exon.seqid, exon.start, exon.end))

            cdss = db.children(transcript.id, featuretype="CDS")
            for cds in cdss:
                t.add_cds(CDS(cds.seqid, cds.start, cds.end))

            transcript_list.append(t)

    gffutils.constants.always_return_list = always_return_list

    return transcript_list


def transcripts_from_pyensembl(db, contig, start, end):
    """
    Utility function to create gene_viz transcript objects from a pyensembl database

    :param db:      Connection to a pyensembl database
    :param contig:  Name of contig to use in query
    :param start:   Start position of query
    :param end:     End position of query
    :return:        A list of gene_viz transcript objects

    example usage
    >>> from gene_viz.utils import transcripts_from_pyensembl
    >>> genome = pyensembl.Genome(
                reference_name="GRCh38",
                annotation_name="Gencode27",
                gtf_path_or_url="gencode.v27.basic.annotation.gtf.gz"
        )
    >>> transcripts = transcripts_from_pyensembl(genome, "chr2", 2210223, 2300331)
    """
    transcript_list = []

    for gene in db.genes_at_locus(contig, start, end):
        for transcript in gene.transcripts:
            t = Transcript(transcript.transcript_name, transcript.gene_id, transcript.contig,
                           transcript.start, transcript.end, transcript.strand)

            for exon in transcript.exons:
                t.add_exon(Exon(exon.id, exon.contig, exon.start, exon.end))

            try:
                for cds in transcript.coding_sequence_position_ranges:
                    t.add_cds(CDS(transcript.contig, cds[0], cds[1]))
            except ValueError:
                pass

            transcript_list.append(t)

    return transcript_list