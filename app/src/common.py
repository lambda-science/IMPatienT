import pandas as pd


def create_feature_list(config_file):
    """Extract the list of feature and format
    them from the configuration file path"""
    feature_df = pd.read_csv(config_file, sep='\t', header=None)
    feature_list = [(row[0].strip().replace(" ", "_"), row[0], row[1])
                    for index, row in feature_df.iterrows()]
    return feature_list


def create_diag_list(config_file):
    """Extract the list of feature and format
    them from the configuration file path"""
    diag_df = pd.read_csv(config_file, sep='\t', header=None)
    diag_list = [(row[0], row[1]) for index, row in diag_df.iterrows()]
    return diag_list


def create_lang_list(config_file):
    """Extract the list of feature and format
    them from the configuration file path"""
    diag_df = pd.read_csv(config_file, sep='\t', header=None)
    diag_list = [(row[0], row[1]) for index, row in diag_df.iterrows()]
    return diag_list


def create_color_list(config_file):
    """Extract the list of coloration type and save as list"""
    with open(config_file) as config_f:
        color_list = config_f.read().splitlines()
    return color_list
