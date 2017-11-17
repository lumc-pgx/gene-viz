"""
Utilities for creating and manipulating data frames
"""
import pandas as pd

def make_data_frame(length, column_names):
    """
    Create a new dataframe with 'length' rows and 'column_names' columns
    :param length: The number of rows to pre-allocate. If None, a zero-length dataframe is created
    :param column_names: A list of column names
    :return: a pandas dataframe
    """
    if length is not None:
        return pd.DataFrame(index=range(length), columns=column_names)
    return pd.DataFrame(columns=column_names)


def transcript_data_frame(length=None):
    """
    A dataframe for storing transcript boundaries
    """
    return make_data_frame(length, ("x0", "y0", "x1", "y1"))


def transcript_label_data_frame(length=None):
    """
    A dataframe for storing gene/transcript id information
    """
    return make_data_frame(length, ("x", "y", "label"))


def exon_data_frame(length=None):
    """
    A dataframe for exons drawn as patches
    """
    return make_data_frame(length, ("x", "y"))


def intron_data_frame(length=None):
    """
    A dataframe for intron / strand direction markers
    """
    return make_data_frame(length, ("x", "y", "angle", "width", "alpha"))


def append_data(dataframe, dataframe_list):
    """
    Append a dataframe to a list of dataframes if the dataframe is not empty
    The original list is modified in-place
    :param dataframe: The dataframe to append
    :param dataframe_list: The list to append the dataframe to
    """
    if dataframe.shape[0] > 0:
        dataframe_list.append(dataframe)


def concat_data(dataframe_list, dataframe_type):
    """
    Concatenate a list of dataframes into a single dataframe
    :param dataframe_list: A list of pandas dataframes
    :param dataframe_type: The type of dataframe to be returned if list is empty
    :return: A single dataframe containing the concatenated data
    """
    return pd.concat(dataframe_list, ignore_index=True) if len(dataframe_list) > 0 else dataframe_type()
