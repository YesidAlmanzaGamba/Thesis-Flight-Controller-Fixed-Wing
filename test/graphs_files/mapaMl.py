import pandas as pd
import folium
import os

# Check the current directory
current_directory = os.getcwd()
print(f"Current Directory: {current_directory}")

# Define the file name
file_name = 'transmision.csv'

# Iterate through directories to find the correct path
for root, dirs, files in os.walk(current_directory):
    if file_name in files:
        file_path = os.path.join(root, file_name)
        break
else:
    raise FileNotFoundError(f"{file_name} not found in any subdirectory of {current_directory}")

print(f"File found: {file_path}")

# Load the CSV file
data = pd.read_csv(file_path)

# Drop rows where all columns are zero
data_cleaned = data.loc[~(data == 0).all(axis=1)]

# Drop rows with NaN values in 'latitud' or 'longitud'
data_cleaned = data_cleaned.dropna(subset=['latitud', 'longitud'])


# Create a folium map centered around the mean latitude and longitude
map_center = map_center = [4.846306, -74.159660]
mymap = folium.Map(location=map_center, zoom_start=10)

# Add points to the map
for _, row in data_cleaned.iterrows():
    if row['latitud'] != 0 and row['longitud'] != 0:
        folium.Marker(location=[row['latitud'], row['longitud']]).add_to(mymap)

# Save the map to an HTML file
output_path = os.path.join(current_directory, 'mapa_prueba.html')
mymap.save(output_path)

print(f"Map saved to {output_path}")