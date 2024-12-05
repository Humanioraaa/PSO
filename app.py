from flask import Flask, render_template, request, redirect, url_for
from script import load_dataset, calculate_distance_matrix, pso_route
import pandas as pd
import folium

app = Flask(__name__)

# Path dataset
DATASET_PATH = "dataset/destinasi-wisata-indonesia.csv"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Ambil koordinat input dari form
        user_lat = float(request.form.get("latitude"))
        user_long = float(request.form.get("longitude"))
        return redirect(url_for("calculate", latitude=user_lat, longitude=user_long))

    # Buat peta menggunakan Folium
    dataset = load_dataset(DATASET_PATH)
    folium_map = folium.Map(location=[-6.2088, 106.8456], zoom_start=12)

    for _, row in dataset.iterrows():
        folium.Marker(
            location=[row["Lat"], row["Long"]],
            popup=row["Place_Name"],
            icon=folium.Icon(color="blue")
        ).add_to(folium_map)

    folium_map.save("templates/map.html")
    return render_template("index.html")

@app.route("/calculate")
def calculate():
    # Ambil koordinat user dari parameter query
    user_lat = float(request.args.get("latitude"))
    user_long = float(request.args.get("longitude"))

    # Load dataset dan tambahkan lokasi user
    dataset = load_dataset(DATASET_PATH)
    user_id = 0
    user_row = pd.DataFrame({
        "Place_Id": [user_id],
        "Place_Name": ["User Location"],
        "Lat": [user_lat],
        "Long": [user_long],
        "Price": [0]
    })
    data_with_user = pd.concat([user_row, dataset], ignore_index=True)

    # Hitung matriks jarak
    distance_matrix = calculate_distance_matrix(data_with_user)

    # Temukan destinasi terdekat dan termurah
    user_distances = distance_matrix.loc[user_id].drop(user_id)
    nearest_5_ids = user_distances.nsmallest(5).index.tolist()
    cheapest_5_ids = dataset.nsmallest(5, "Price")['Place_Id'].tolist()

    nearest_matrix = distance_matrix.loc[nearest_5_ids, nearest_5_ids]
    cheapest_matrix = distance_matrix.loc[cheapest_5_ids, cheapest_5_ids]

    nearest_route, nearest_distance = pso_route(nearest_5_ids, nearest_matrix)
    cheapest_route, cheapest_distance = pso_route(cheapest_5_ids, cheapest_matrix)

    nearest_route_names = data_with_user[data_with_user['Place_Id'].isin(nearest_route)]['Place_Name'].tolist()
    cheapest_route_names = data_with_user[data_with_user['Place_Id'].isin(cheapest_route)]['Place_Name'].tolist()

    return render_template(
        "result.html",
        nearest_route=nearest_route_names,
        nearest_distance=nearest_distance,
        cheapest_route=cheapest_route_names,
        cheapest_distance=cheapest_distance,
    )

if __name__ == "__main__":
    app.run(debug=True)