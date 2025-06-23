import json
import os
import random
from math import pow

import numpy as np
from flask import current_app


def boqa(alpha, beta, query, items_stat):
    """Implementation of the BOQA algorithm.

    Args:
        alpha (float): False positive rate.
        beta (float): False negative rate.
        query (dict): Dict of query terms (standard terms). Key: term name, value: presence value
        items_stat (dict): Dictionnary of items statistics. Key: disease, Value: list of items

    Returns:
        [dict]: Dictionnary of disease and their prediction probability.
    """
    hidden = {}
    p = {}
    a = {}
    a_init = 0
    # For each disease
    for disease in items_stat:
        # We initiliaze Hidden Layer with values from the stats
        for term in query:
            if term in items_stat[disease]["feature"].keys():
                proba = items_stat[disease]["feature"][term]
                hidden[term] = np.random.choice([1, 0], p=[proba, 1 - proba])
            else:
                hidden[term] = 0
        # Cardinality calculation of terms between H and Q
        m = matrix_m(query, hidden)
        a[disease] = (
                pow(beta, m[0, 1])
                * pow(1 - beta, m[1, 1])
                * pow(1 - alpha, m[0, 0])
                * pow(alpha, m[1, 0])
        )
        a_init += a[disease]
    for disease in items_stat:
        p[disease] = a[disease] / a_init
    return p


def matrix_m(Q, H):
    """Return the 2x2 matrix of the overlap between Query layer and Hidden (model) layer.

    Args:
        Q (dict): Dict of query terms (standard terms). Key: term name, value: presence value
        H (dict): Dict of hidden terms (model terms for a given disease). Key: term name, value: presence value

    Raises:
        Exception: If Q and H keys are not the same: raise exception.

    Returns:
        numpy array: 2x2 matrix of the overlap between Query layer and Hidden (model) layer.
    """
    matrix_count = np.empty((2, 2))
    if Q.keys() != H.keys():
        raise Exception("Error Ontology not matching stats")
    for x in range(2):
        for y in range(2):
            count = 0
            for i in Q:
                if Q[i] == x and H[i] == y:
                    count += 1
            matrix_count[x, y] = count
    return matrix_count


def subsample_query(query):
    """NOT USED: Subsample query to six terms only taken randomly. (From Publication)

    Args:
        query (dict): Dict of query terms (standard terms). Key: term name, value: presence value

    Returns:
        [dict]: Dict of six query terms (standard terms).
    """
    query_filt = {k: v for k, v in query.items() if v == 1}
    try:
        keys = random.sample(list(query_filt), 6)
    except:
        keys = query_filt

    for k in query.keys():
        if k not in keys:
            query[k] = 0
    return query


def boqa_monte_carlo(query, items_stat, n_indiv=50, alpha=0.001, beta=0.05):
    """Run the BOQA algorithm a number of time and average the results.
    Return a list of tuple for each disease and the frequency of time they appeared as the best prediction.

    Args:
        query (dict): Dict of query terms (standard terms). Key: term name, value: presence value
        items_stat (dict): Dictionnary of items statistics. Key: disease, Value: list of items
        n_indiv (int, optional): Number of time the algo is executed. Defaults to 50.
        alpha (float, optional): False positive rate. Defaults to 0.0001.
        beta (float, optional): False negative rate. Defaults to 0.3.

    Returns:
        list of tuple: List of tuple of disease and the frequency of time they appeared as the best prediction.
    """
    results = []
    for _ in range(n_indiv):
        result = boqa(alpha, beta, query, items_stat)
        for key, value in result.items():
            if value > 0.5:
                results.append(key)
    dd = {x: results.count(x) for x in set(results)}
    return [max(dd, key=dd.get), max(dd.values()) / n_indiv]


def get_boqa_pred(tree: str):
    """Calculate the prediction of the BOQA algorithm based on the standard vocabulary tree using the Monte Carlo method.

    Args:
        tree (str): JSON string of the standard vocabulary tree for the patient.

    Returns:
        list of tuple: List of tuple of disease and the frequency of time they appeared as the best prediction.
    """
    items_stat = json.load(
        open(os.path.join(current_app.config["VIZ_FOLDER"], "stat_per_diag.json"), "r")
    )
    items_stat.pop("OTHER", None)
    items_stat.pop("UNCLEAR", None)
    my_tree = json.loads(tree)
    query = {}
    replace_dict = {-0.25: 0, 0.25: 1, 0.5: 1, 0.75: 1, 1: 1, 0: 0}
    for feature in my_tree:
        value = float(feature["data"].get("presence", -0.25))
        query[feature["id"]] = replace_dict[value]
    best_match = boqa_monte_carlo(query, items_stat)
    return best_match
