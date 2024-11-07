import pandas as pd
import folium
import os
import numpy as np
from scipy.interpolate import interp1d

# Check the current directory
current_directory = os.getcwd()
print(f"Current Directory: {current_directory}")

# Define the file name
file_name = 'avion.csv'

# Iterate through directories to find the correct path
for root, dirs, files in os.walk(current_directory):
    if file_name in files:
        file_path = os.path.join(root, file_name)
        break
else:
    raise FileNotFoundError(f"{file_name} not found in any subdirectory of {current_directory}")

print(f"File found: {file_path}")

# Load the CSV file
try:
    data = pd.read_csv(file_path, on_bad_lines='warn')
except pd.errors.ParserError as e:
    print(f"Error parsing CSV file: {e}")
    raise

# Drop rows where all columns are zero
data_cleaned = data.loc[~(data == 0).all(axis=1)]

# Drop rows with NaN values in 'latitud' or 'longitud'
data_cleaned = data_cleaned.dropna(subset=['latitud', 'longitud'])

# Ensure latitud and longitud columns are strings for filtering
data_cleaned['latitud'] = data_cleaned['latitud'].astype(str)
data_cleaned['longitud'] = data_cleaned['longitud'].astype(str)

# Filter rows where latitude starts with '4' and longitude starts with '-74'
data_cleaned = data_cleaned[data_cleaned['latitud'].str.startswith('4')]
data_cleaned = data_cleaned[data_cleaned['longitud'].str.startswith('-74')]

# Convert latitud and longitud back to float for mapping
data_cleaned['latitud'] = data_cleaned['latitud'].astype(float)
data_cleaned['longitud'] = data_cleaned['longitud'].astype(float)

# Interpolation function to generate more points
def interpolate_points(data, num_points=2):
    try:
        latitudes = data['latitud'].values
        longitudes = data['longitud'].values
        distance = np.cumsum(np.sqrt(np.diff(latitudes)**2 + np.diff(longitudes)**2))
        distance = np.insert(distance, 0, 0)  # Add 0 at the beginning

        alpha = np.linspace(0, distance[-1], num_points * len(latitudes))
        interp_lat = interp1d(distance, latitudes, kind='linear')(alpha)
        interp_long = interp1d(distance, longitudes, kind='linear')(alpha)
        
        return pd.DataFrame({'latitud': interp_lat, 'longitud': interp_long})
    except Exception as e:
        print(f"Error during interpolation: {e}")
        return pd.DataFrame(columns=['latitud', 'longitud'])

# Interpolate points
data_interpolated = interpolate_points(data_cleaned)

# Create a folium map centered around the specified coordinates with a higher zoom level
map_center = [4.846306, -74.159660]
mymap = folium.Map(location=map_center, zoom_start=35)

# Add markers for the start and end points with legends
if not data_interpolated.empty:
    folium.Marker(location=[data_interpolated.iloc[0]['latitud'], data_interpolated.iloc[0]['longitud']],
                  popup='Inicio', icon=folium.Icon(color='green')).add_to(mymap)
    folium.Marker(location=[data_interpolated.iloc[-1]['latitud'], data_interpolated.iloc[-1]['longitud']],
                  popup='Final', icon=folium.Icon(color='red')).add_to(mymap)

    # Add lines connecting the points
    points = data_interpolated[['latitud', 'longitud']].values.tolist()
    folium.PolyLine(points, color='blue').add_to(mymap)
else:
    print("Interpolation failed, no points to plot on map.")

# Save the map to an HTML file
output_path = os.path.join(current_directory, 'mapa_transmision.html')
mymap.save(output_path)

print(f"Map saved to {output_path}")
