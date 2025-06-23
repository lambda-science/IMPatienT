import pandas as pd


def create_diag_list(config_file):
    """Extract the list of feature and format
    them from the configuration file path"""
    diag_df = pd.read_csv(config_file, sep="\t", header=None)
    diag_list = [(row[0], row[1]) for index, row in diag_df.iterrows()]
    return diag_list


def create_list(config_file):
    """Extract the list of a file and save as list"""
    with open(config_file) as config_f:
        elem_list = config_f.read().splitlines()
    return elem_list
