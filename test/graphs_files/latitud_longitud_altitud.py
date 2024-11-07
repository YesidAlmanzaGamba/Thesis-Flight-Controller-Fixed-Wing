import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

# Check the current directory
current_directory = os.getcwd()
print(f"Current Directory: {current_directory}")

# Define the file name
file_name = 'transmision_1.csv'

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

# Drop rows with NaN values in 'latitud', 'longitud' o 'altitud'
data_cleaned = data_cleaned.dropna(subset=['latitud', 'longitud', 'altitud'])

# Ensure latitud and longitud columns are strings for filtering
data_cleaned['latitud'] = data_cleaned['latitud'].astype(str)
data_cleaned['longitud'] = data_cleaned['longitud'].astype(str)

# Filter rows where latitude starts with '4' and longitude starts with '-74'
data_cleaned = data_cleaned[data_cleaned['latitud'].str.startswith('4')]
data_cleaned = data_cleaned[data_cleaned['longitud'].str.startswith('-74')]

# Convert latitud, longitud and altitud back to float for mapping
data_cleaned['latitud'] = data_cleaned['latitud'].astype(float)
data_cleaned['longitud'] = data_cleaned['longitud'].astype(float)
data_cleaned['altitud'] = data_cleaned['altitud'].astype(float)

# Ensure the altitud starts from 1550
data_cleaned = data_cleaned[data_cleaned['altitud'] >= 1550]

# Create 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the data with lines connecting the points
ax.plot(data_cleaned['latitud'], data_cleaned['longitud'], data_cleaned['altitud'], color='red', marker='o', markersize=2)

# Highlight the first 1000 ascent lines and last 1000 descent lines
datos_ini = 3950
datos_fini = 5650

ax.plot(data_cleaned['latitud'].head(datos_ini), data_cleaned['longitud'].head(datos_ini), data_cleaned['altitud'].head(datos_ini), color='blue', marker='o', markersize=2, label='Ascenso')
ax.plot(data_cleaned['latitud'].tail(datos_fini), data_cleaned['longitud'].tail(datos_fini), data_cleaned['altitud'].tail(datos_fini), color='green', marker='o', markersize=2, label='Descenso')

# Set axis labels with padding
ax.set_xlabel('Latitud (°)', labelpad=40)
ax.set_ylabel('Longitud (°)', labelpad=40)
ax.set_zlabel('Altitud (metros)', labelpad=20)

# Set axis label font sizes
ax.xaxis.label.set_size(14)
ax.yaxis.label.set_size(14)
ax.zaxis.label.set_size(14)

# Rotate tick labels for better readability and set limits for significant figures
ax.set_xticks([round(x, 6) for x in ax.get_xticks()])
ax.set_yticks([round(y, 6) for y in ax.get_yticks()])
ax.set_zticks([round(z, 1) for z in ax.get_zticks()])

ax.set_xticklabels([f'{x:.6f}' for x in ax.get_xticks()], rotation=45, ha='right')
ax.set_yticklabels([f'{y:.6f}' for y in ax.get_yticks()], rotation=-45, ha='left')
ax.set_zticklabels([f'{z:.1f}' for z in ax.get_zticks()], rotation=0, ha='center')

# Set axis tick label font sizes
ax.tick_params(axis='both', which='major', labelsize=10)
ax.tick_params(axis='both', which='minor', labelsize=8)

# Set specific view angle
ax.view_init(elev=25, azim=63)

# Add legend
ax.legend()

# Adjust layout to ensure labels are not overlapped
plt.tight_layout()

plt.title('Latitud y Longitud vs Altitud')
plt.show()
