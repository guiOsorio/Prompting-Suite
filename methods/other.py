## TEST OPTIMAL N HYPERPARAMETER FOR KMEANS CLUSTERING IN AUTO_COT

import random
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
import matplotlib.pyplot as plt
import hdbscan

from CoT import cot_examples

def test_n_kmeans():
    # Load strings then shuffle them
    all_shots = [item for sublist in cot_examples.values() for item in sublist]
    random.shuffle(all_shots)

    # Convert strings to vectors using MiniLM (384-dimensional vectors)
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    embeds = model.encode(all_shots)

    # KMeans clustering - test range of n 1 to 50 in increments of 5
    n_clusters_range = [1] + [i for i in range(5, 51, 5)]
    inertia = []
    for n_clusters in n_clusters_range:
        kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(embeds)
        inertia.append(kmeans.inertia_)

    # Plot the Elbow curve
    plt.figure()
    plt.plot(n_clusters_range, inertia, marker='o')
    plt.title('Elbow Method For Optimal n_clusters')
    plt.xlabel('Number of clusters')
    plt.ylabel('Inertia')
    plt.show()

def evaluate_kmeans():
    strings_list = []
    true_labels = []
    for category, examples in cot_examples.items():
        for example in examples:
            strings_list.append(example)
            true_labels.append(category)

    # Load strings then shuffle them
    all_shots = [item for sublist in cot_examples.values() for item in sublist]
    random.shuffle(all_shots)

    # Convert strings to vectors using MiniLM (384-dimensional vectors)
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    embeds = model.encode(all_shots)

    # Use KMeans to cluster the embeddings
    n_clusters = 10  # See file other.py for determining this hyperparameter
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(embeds)

    # Compute Clustering Evaluation Metrics
    ari = adjusted_rand_score(true_labels, kmeans.labels_)
    nmi = normalized_mutual_info_score(true_labels, kmeans.labels_, average_method='arithmetic')

    # Output the results
    print(f'Adjusted Rand Index: {ari:.2f}')
    print(f'Normalized Mutual Information: {nmi:.2f}')

def evaluate_agg_clustering():
    strings_list = []
    true_labels = []
    for category, examples in cot_examples.items():
        for example in examples:
            strings_list.append(example)
            true_labels.append(category)

    # Load strings then shuffle them
    all_shots = [item for sublist in cot_examples.values() for item in sublist]
    random.shuffle(all_shots)

    # Convert strings to vectors using MiniLM (384-dimensional vectors)
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    embeds = model.encode(all_shots)

    agg_clustering = AgglomerativeClustering(n_clusters=10, linkage='ward')
    agg_labels = agg_clustering.fit_predict(embeds)

    # Compute Clustering Evaluation Metrics
    ari = adjusted_rand_score(true_labels, agg_labels)
    nmi = normalized_mutual_info_score(true_labels, agg_labels, average_method='arithmetic')

    # Output the results
    print(f'Adjusted Rand Index: {ari:.2f}')
    print(f'Normalized Mutual Information: {nmi:.2f}')

def evaluate_hdbscan():
    strings_list = []
    true_labels = []
    for category, examples in cot_examples.items():
        for example in examples:
            strings_list.append(example)
            true_labels.append(category)

    # Load strings then shuffle them
    all_shots = [item for sublist in cot_examples.values() for item in sublist]
    random.shuffle(all_shots)

    # Convert strings to vectors using MiniLM (384-dimensional vectors)
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    embeds = model.encode(all_shots)

    clusterer = hdbscan.HDBSCAN(min_cluster_size=3)
    cluster_labels = clusterer.fit_predict(embeds)

    # Compute Clustering Evaluation Metrics
    ari = adjusted_rand_score(true_labels, cluster_labels)
    nmi = normalized_mutual_info_score(true_labels, cluster_labels, average_method='arithmetic')

    # Output the results
    print(f'Adjusted Rand Index: {ari:.2f}')
    print(f'Normalized Mutual Information: {nmi:.2f}')