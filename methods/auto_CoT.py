# Implements modified version of Auto-CoT, where instead of starting with a question, we start examples.
# Therefore, the algorithm here consists of clustering the CoT examples and picking a random example from each cluster to add to the prompt.

import os
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
import random
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans, AgglomerativeClustering
import hdbscan

from .CoT import cot_examples

# Load strings then shuffle them
all_shots = [item for sublist in cot_examples.values() for item in sublist]
random.shuffle(all_shots)

clustering_methods = ['kmeans', 'agg', 'hdbscan']

def cluster_cot(clustering_method, data=all_shots):
    # Convert strings to vectors using MiniLM (384-dimensional vectors)
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    embeds = model.encode(data)

    if clustering_method == 'kmeans':
        # KMeans - n of 10 was used based on analysis of the elbow method (see other.py file for more info)
        n_clusters = 10
        cluster_labels = KMeans(n_clusters=n_clusters, n_init=10, random_state=0).fit_predict(embeds)
    elif clustering_method == 'agg':
        # Agglomerative Clustering - n of 10 as well
        n_clusters = 10
        agg = AgglomerativeClustering(n_clusters=n_clusters)
        cluster_labels = agg.fit_predict(embeds)
    elif clustering_method == 'hdbscan':
        # HDBSCAN - min_cluster_size of 3 seemed appropriate based on familiarity with the data. Note that HDBSCAN does not assign each point to a cluster, with outliers having the label -1
        clusterer = hdbscan.HDBSCAN(min_cluster_size=3)
        cluster_labels = clusterer.fit_predict(embeds)
    else:
        raise TypeError(f"Invalid clustering method selected. The allowed clustering methods are one of ['kmeans', 'agg', 'hdbscan']")

    return list(cluster_labels)

def select_shots(cluster_labels):
    # Pick a random index of cluster_labels for each cluster
    cluster_indices = {}
    for idx, label in enumerate(cluster_labels):
        if label != -1:  # Ignore cluster -1
            cluster_indices.setdefault(label, []).append(idx)
    random_indices = [random.choice(indices) for indices in cluster_indices.values()]

    # Select a shot from each cluster based on random_indices
    selected_shots = [all_shots[idx] for idx in random_indices]

    return selected_shots

# Takes both functions above and merges it into one
def auto_cot(clustering_method):
    cluster_labels = cluster_cot(clustering_method)
    selected_shots = select_shots(cluster_labels)

    return selected_shots

# Creates a few-shot prompt based on the modified auto-cot algorithm defined above. To be exported and used in main
def create_autocot_prompt(clustering_method):
    selected_shots = auto_cot(clustering_method)
    prompt_beg = "Here are some examples of questions answered in a step-by-step manner.\n"
    prompt_end = "\nAnswer the following question in a step-by-step manner, where the last step outputs the final answer. Clearly state what the final answer is."

    prompt = prompt_beg
    for shot in selected_shots:
        prompt += shot
    prompt += prompt_end

    return prompt

