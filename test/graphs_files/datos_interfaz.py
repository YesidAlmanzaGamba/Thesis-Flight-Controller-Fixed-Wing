import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import json

# Check the current directory
current_directory = os.getcwd()
print(f"Current Directory: {current_directory}")

# Load the JSON file
file_path = 'src/Pruebas/DatosUAV.json'
with open(file_path, 'r') as file:
    data = json.load(file)

# Convert the JSON data to a DataFrame
df = pd.DataFrame(data)

# Remove rows with duplicate 'tiempo' values
df_cleaned = df.drop_duplicates(subset='tiempo')

# Ensure 'tiempo' is sorted
df_cleaned = df_cleaned.sort_values(by='tiempo')

# Remove 'velocidad' column if exists
if 'velocidad' in df_cleaned.columns:
    df_cleaned = df_cleaned.drop(columns=['velocidad'])

# Define the columns to ignore zero values
columns_to_ignore_zero = ['altitud', 'temperatura', 'presion']

# Replace zero values with NaN for the specified columns
df_cleaned[columns_to_ignore_zero] = df_cleaned[columns_to_ignore_zero].replace(0, np.nan)

# Interpolate data to have intermediate time values
time_new = np.arange(df_cleaned['tiempo'].min(), df_cleaned['tiempo'].max(), 0.1)
df_interpolated = pd.DataFrame({'tiempo': time_new})

# Define the order of columns
columns_order = ['altitud', 'temperatura', 'presion', 'yaw', 'pitch', 'roll']

# Filter and sort columns based on the defined order
columns_to_interpolate = [col for col in columns_order if col in df_cleaned.columns]

# Interpolate each column
for col in columns_to_interpolate:
    df_interpolated[col] = np.interp(time_new, df_cleaned['tiempo'], df_cleaned[col].interpolate().dropna())

# List of colors for the plots
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

# Create subplots for each column vs. 'tiempo'
num_columns = len(columns_to_interpolate)
fig, axs = plt.subplots(num_columns, 1, figsize=(10, num_columns * 2), sharex=True)

# Define labels with units
labels_with_units = {
    'altitud': 'Altitud (m)',
    'temperatura': 'Temperatura (°C)',
    'presion': 'Presión (hPa)',
    'yaw': 'Yaw (°)',
    'pitch': 'Pitch (°)',
    'roll': 'Roll (°)'
}

for i, col in enumerate(columns_to_interpolate):
    color = colors[i % len(colors)]
    axs[i].plot(df_interpolated['tiempo'], df_interpolated[col], color=color, label=f'{labels_with_units[col]} - Original')
    axs[i].set_ylabel(labels_with_units[col])
    axs[i].grid(True)
    axs[i].legend(loc='upper right')
    axs[i].set_xlabel('Tiempo (s)')
    axs[i].set_title(f'{labels_with_units[col]} vs Tiempo')

plt.suptitle('Variables Interpoladas vs Tiempo')
plt.tight_layout(rect=[0, 0, 1, 0.97])

# Save the combined plot
combined_plot_path = os.path.join(current_directory, 'subplots_interpolated.png')
plt.savefig(combined_plot_path)
plt.show()

print(f"Combined plot has been saved in: {combined_plot_path}")
