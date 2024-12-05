import pandas as pd
import numpy as np
from geopy.distance import geodesic

def load_dataset(file_path):
    dataset = pd.read_csv(file_path)
    dataset['Coordinate'] = dataset['Coordinate'].apply(eval)
    dataset['Lat'] = dataset['Coordinate'].apply(lambda x: x['lat'])
    dataset['Long'] = dataset['Coordinate'].apply(lambda x: x['lng'])
    return dataset

def calculate_distance_matrix(data):
    num_places = len(data)
    distance_matrix = pd.DataFrame(index=data['Place_Id'], columns=data['Place_Id'], dtype=float)
    for i in range(num_places):
        for j in range(num_places):
            coord1 = (data.iloc[i]['Lat'], data.iloc[i]['Long'])
            coord2 = (data.iloc[j]['Lat'], data.iloc[j]['Long'])
            distance_matrix.iloc[i, j] = geodesic(coord1, coord2).kilometers
    return distance_matrix

def calculate_total_distance(route, matrix):
    total_distance = 0
    for i in range(len(route) - 1):
        total_distance += matrix.iloc[route[i], route[i + 1]]
    total_distance += matrix.iloc[route[-1], route[0]]
    return total_distance

def pso_route(subset_ids, matrix, max_iter=100, num_particles=30):
    num_places = len(subset_ids)
    particles = [np.random.permutation(num_places) for _ in range(num_particles)]
    personal_best = particles.copy()
    personal_best_scores = [calculate_total_distance(p, matrix) for p in particles]
    global_best = personal_best[np.argmin(personal_best_scores)]
    global_best_score = min(personal_best_scores)

    for _ in range(max_iter):
        for i in range(num_particles):
            r1, r2 = np.random.rand(num_places), np.random.rand(num_places)
            swap_indices = np.argsort(r1 + r2)
            for idx in swap_indices[:2]:
                particles[i][idx], particles[i][idx - 1] = particles[i][idx - 1], particles[i][idx]

            current_score = calculate_total_distance(particles[i], matrix)
            if current_score < personal_best_scores[i]:
                personal_best[i] = particles[i].copy()
                personal_best_scores[i] = current_score
            if current_score < global_best_score:
                global_best = particles[i].copy()
                global_best_score = current_score

    optimal_route = [subset_ids[i] for i in global_best]
    return optimal_route, global_best_score
