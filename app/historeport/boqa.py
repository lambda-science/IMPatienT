from math import pow
import json
import random
import numpy as np
import os
from flask import current_app


def boqa(alpha, beta, query, items_stat):
    hidden = {}
    p = {}
    a = {}
    a_init = 0
    # Pour chaque maladie
    for disease in items_stat:
        # On initialise de Hidden Layer avec les valeurs de stats
        for term in query:
            if term in items_stat[disease]["feature"].keys():
                proba = items_stat[disease]["feature"][term] / 100
                hidden[term] = np.random.choice([1, 0], p=[proba, 1 - proba])
            else:
                hidden[term] = 0
        # On calcul la cardinalité des termes H et Q
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
    query_filt = {k: v for k, v in query.items() if v == 1}
    try:
        keys = random.sample(list(query_filt), 6)
    except:
        keys = query_filt

    for k in query.keys():
        if k not in keys:
            query[k] = 0
    return query


def propagate_annotations(query):
    pass


def boqa_monte_carlo(query, items_stat, n_indiv=50, alpha=0.0001, beta=0.3):
    results = []
    for _ in range(n_indiv):
        result = boqa(alpha, beta, query, items_stat)
        for key, value in result.items():
            if value > 0.5:
                results.append(key)
    dd = {x: results.count(x) for x in set(results)}
    return [max(dd, key=dd.get), max(dd.values()) / n_indiv]


def get_boqa_pred(tree: str):
    items_stat = json.load(
        open(os.path.join(current_app.config["VIZ_FOLDER"], "stat_per_diag.json"), "r")
    )
    items_stat.pop("OTHER", None)
    my_tree = json.loads(tree)
    query = {}
    replace_dict = {-0.25: 0, 0.25: 1, 0.5: 1, 0.75: 1, 1: 1, 0: 0}
    for feature in my_tree:
        value = float(feature["data"].get("presence", -0.25))
        query[feature["text"]] = replace_dict[value]
    best_match = boqa_monte_carlo(query, items_stat)
    return best_match
