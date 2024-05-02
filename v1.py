import numpy as np
import tkinter as tk
from tkinter import messagebox
import os
import colorsys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tempfile
import atexit


def create_lab_color_chart(L_values, a_values, b_values, image_path):
     try:
         # Load the image
         image = plt.imread(image_path)

         # Create a figure and an axis
         fig, ax = plt.subplots()

         # Display the image as the graph background
         ax.imshow(image, extent=[-100, 100, -100, 100], alpha=1)

         # Scatter plot for LAB color points
         scatter = ax.scatter(
             a_values, b_values,
             color=['none' if L >= 0 and a >= 0 else 'none' for L, a in zip(L_values, a_values)],
             edgecolors='black', linewidths=1.5
         )

         # Note points on the graph
         for i, txt in enumerate(zip(L_values, a_values)):
             ax.annotate(f'({txt[0]};{txt[1]})', (L_values[i], a_values[i]), textcoords="offset points",
                         xytext=(0, 5), ha='center', va='bottom')

         # Add labels and title
         ax.set_ylabel('a*')
         ax.set_xlabel('b*')
         ax.set_title('CIELab')

         # Add reference lines for the X and Y axes
         ax.axhline(0, color='black', linewidth=0.7, linestyle='--')
         ax.axvline(0, color='black', linewidth=0.5, linestyle='--')

         # Grid settings
         plt.grid(True, linestyle='--', alpha=0.6)

         # Define axis limits
         ax.set_xlim(-100, 100)
         ax.set_ylim(-100, 100)

         # Add a black and white gradient bar
         cax = fig.add_axes([0.85, 0.1, 0.04, 0.79])
         cmap = plt.cm.gray
         norm = plt.Normalize(0, 100)
         cb = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm), cax=cax)
         cb.set_label('L*')

         # Add a point to the color bar
         for L in L_values:
             normalized_point = L
             cb.ax.plot([0, 1], [normalized_point, normalized_point],
                        color='red', linewidth=5, marker='_', markersize=8, label='Manual Point')

         # Add the image to the list of images
         figures.append(fig)

         # Display the graph
         plt.show()

     except Exception as e:
         messagebox.showerror("Error", f"Error displaying chart: {str(e)}")


def generate_color_wheel():
     num_points = 360
     hues = np.linspace(0, 1, num_points)
     saturations = np.linspace(0, 1, num_points)
     lightness = 0.5 # Brightness at 50%

     # Create a 2D grid of values
     hsl_values = np.array([[hue, saturation, lightness]
                           for hue in hues for saturation in saturations])

     # Convert to RGB
     rgb_values = np.array([colorsys.hls_to_rgb(h, l, s)
                           for h, s, l in hsl_values])

     # Reshape arrays for plotting
     hues = hsl_values[:, 0].reshape((num_points, num_points))
     saturations = hsl_values[:, 1].reshape((num_points, num_points))
     rgb_values = rgb_values.reshape((num_points, num_points, 3))

     # Plots the color wheel adjusted to the LAB color space
     fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))
     ax.set_theta_direction(1)
     ax.set_theta_offset(np.pi / 6.0)
     ax.set_position([0, 0, 1, 1]) # Adjust position and size
     ax.set_rlabel_position(1)

     # Add scale from 0 to 100 along the radius
     r_ticks = np.linspace(0, 1, 6)
     r_labels = [f'{int(t*100)}' for t in r_ticks]
     ax.set_yticks(r_ticks)
     ax.set_yticklabels(r_labels, color='gray', fontsize=8)

     c = ax.pcolormesh(hues * 2 * np.pi, saturations, rgb_values)

     # Remove labels and gridlines from axes
     ax.set_xticklabels([])
     ax.set_yticklabels([])
     ax.grid(False)

     # Function to delete the temporary file when closing the program
     def delete_temporary_file(file_path):
         os.unlink(file_path)

     # Create a temporary file
     with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
         image_path = temp_file.name

     # Save the generated graph as an image file
     image_path = 'color_wheel.png'
     plt.savefig(image_path, dpi=100, bbox_inches='tight', pad_inches=0)
     plt.close()

     # Register the function to delete the temporary file when the program closes
     atexit.register(delete_temporary_file, image_path)

     return image_path

def main():
     # Create the main window
     root = tk.Tk()
     root.title("LAB Color Chart")

     # Define the window icon
    # root.iconbitmap("C:/Users/arlie/OneDrive/CIELAB/TESTE/CIELAB.ico")

     # Label for instruction
     version_label = tk.Label(
         root, text='Enter the values of L*a*b*:', font=('Arial Bold', 9))
     version_label.pack(expand=True)

     # Define the window dimensions
     window_width = 400
     window_height = 200

     # Get the dimensions of the screen
     screen_width = root.winfo_screenwidth()
     screen_height = root.winfo_scree