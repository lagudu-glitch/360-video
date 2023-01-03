# Copyright 2022 Vishnu Lagudu - License: MIT License

import math as m
import numpy as np
import pandas as pd
# from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from scipy.spatial.transform import Rotation as R

def get_euler (data):
    euler = []
    for i in range (0, len(data), 10):
        value = [0, 0, 0]
        value[0] = np.mean (data[i:i+10,3])
        value[1] = np.mean (data[i:i+10,4])
        value[2] = np.mean (data[i:i+10,5])
        euler.append(value)

    return euler

def read (f_name):
    data = open (f_name)
    result = np.genfromtxt (data, delimiter=",")
    # exchange yaw and pitch
    result [:, [3, 4]] = result [:, [4, 3]]
    euler = get_euler (result[1::])

    return euler

def degree_rot (euler_set_1, euler_set_2):
    # calculates the degree of rotation
    r1 = R.from_euler('zyx', euler_set_1, degrees=True)
    r2 = R.from_euler('zyx', euler_set_2, degrees=True)
    r = np.matmul (np.transpose(r1.as_matrix()), r2.as_matrix())
    val = (np.trace(r) - 1) / 2
    if (val > 1):
        val = 1
    angle = np.arccos (val)

    return angle

def find_panning (eulers):
    idx_1 = idx_2 = 0
    all_pans = []
    for i in range (1, len(eulers)):
        angle = degree_rot (eulers[i - 1], eulers[i])
        if (angle > 0.1):
            idx_2 = idx_2 + 1
            continue

        if (idx_1 != idx_2):
            all_pans.append([idx_1, idx_2])
            idx_1 = idx_2
        idx_1 = idx_1 + 1
        idx_2 = idx_2 + 1

    return all_pans

def net_rot (eulers, pan):
    rotation = 0
    for idx in range (pan[0] + 1, pan[1] + 1):
        rotation = rotation + degree_rot (eulers[idx - 1], eulers[idx])

    return rotation


def create_feature_vectors (eulers):
    all_feature_vector = [] 
    all_pans = find_panning (eulers)
    for pan in all_pans:
        feature_vector = [0, 0, 0]
        time = pan[1] - pan [0] + 1
        rotation = net_rot (eulers, pan)
        angular_speed = rotation / time

        feature_vector = [time, rotation, angular_speed]

        all_feature_vector.append(feature_vector)
    
    return all_feature_vector

def optimal_K (K, feature_vectors):
    distortions = []
    for k in K:
        Kmean = KMeans (n_clusters=k)
        Kmean.fit (feature_vectors)
        distortions.append (Kmean.inertia_)
    
    return distortions

# Make random data
eulers = read ("interaction_event.csv")
feature_vectors = create_feature_vectors (eulers)

# Make a clusturs
K = range (1, 10)
# plt.figure (figsize=(16,8))
distortions = optimal_K (K, feature_vectors)
plt.plot (K, distortions, 'bx-')
plt.xlabel ('K values')
plt.ylabel ('Distortion')
plt.title ('Elbow Plot')
plt.show ()

Kmean = KMeans (n_clusters=4, random_state=0)
Kmean.fit (feature_vectors)
centers = Kmean.cluster_centers_
print (centers)
labels = Kmean.labels_

cluster1 = 0
cluster2 = 0
cluster3 = 0
cluster4 = 0

fig = plt.figure(figsize = (8,8))
ax = fig.add_subplot(111, projection='3d')
for i in range (0, len(labels)):
    if (labels[i] == 0):
        ax.scatter(feature_vectors[i][0],feature_vectors[i][1],feature_vectors[i][2], s = 40 , color = 'blue')
    elif (labels[i] == 1):
        ax.scatter(feature_vectors[i][0],feature_vectors[i][1],feature_vectors[i][2], s = 40 , color = 'orange')
    elif (labels[i] == 2):
        ax.scatter(feature_vectors[i][0],feature_vectors[i][1],feature_vectors[i][2], s = 40 , color = 'green')
    elif (labels[i] == 3):
        ax.scatter(feature_vectors[i][0],feature_vectors[i][1],feature_vectors[i][2], s = 40 , color = 'purple')
plt.scatter(centers[:, 0], centers[:, 1], c='black', s=200, alpha=0.5)
ax.set_xlabel('Time')
ax.set_ylabel('Rotation')
ax.set_zlabel('Angular Speed')
ax.set_title ('K - means Clusters')
# ax.legend(['Cluster 1', 'Cluster 2', 'Cluster 3', 'Cluster 4'], [cluster1, cluster2, cluster3, cluster4], loc='upper left')
plt.show()
