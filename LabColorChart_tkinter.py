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
            a_values,
            b_values,
            color=["none" if L >= 0 and a >= 0 else "none" for L, a in zip(L_values, a_values)],
            edgecolors="black",
            linewidths=1.5,
        )

        # Note points on the graph
        for i, txt in enumerate(zip(a_values, b_values)):
            ax.annotate(
                f"({txt[0]};{txt[1]})",
                (a_values[i], b_values[i]),
                textcoords="offset points",
                xytext=(0, 5),
                ha="center",
                va="bottom",
            )

        # Add labels and title
        ax.set_ylabel("a*")
        ax.set_xlabel("b*")
        ax.set_title("CIELab")

        # Add reference lines for the X and Y axes
        ax.axhline(0, color="black", linewidth=0.7, linestyle="--")
        ax.axvline(0, color="black", linewidth=0.5, linestyle="--")

        # Grid settings
        plt.grid(True, linestyle="--", alpha=0.6)

        # Define axis limits
        ax.set_xlim(-100, 100)
        ax.set_ylim(-100, 100)

        # Add a black and white gradient bar
        cax = fig.add_axes([0.85, 0.1, 0.04, 0.79])
        cmap = plt.cm.gray
        norm = plt.Normalize(0, 100)
        cb = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm), cax=cax)
        cb.set_label("L*")

        # Add a point to the color bar
        for L in L_values:
            normalized_point = L
            cb.ax.plot(
                [0, 1],
                [normalized_point, normalized_point],
                color="red",
                linewidth=5,
                marker="_",
                markersize=8,
                label="Manual Point",
            )

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
    lightness = 0.5  # Brightness at 50%

    # Create a 2D grid of values
    hsl_values = np.array([[hue, saturation, lightness] for hue in hues for saturation in saturations])

    # Convert to RGB
    rgb_values = np.array([colorsys.hls_to_rgb(h, l, s) for h, s, l in hsl_values])

    # Reshape arrays for plotting
    hues = hsl_values[:, 0].reshape((num_points, num_points))
    saturations = hsl_values[:, 1].reshape((num_points, num_points))
    rgb_values = rgb_values.reshape((num_points, num_points, 3))

    # Plots the color wheel adjusted to the LAB color space
    fig, ax = plt.subplots(subplot_kw=dict(projection="polar"))
    ax.set_theta_direction(1)
    ax.set_theta_offset(np.pi / 6.0)
    ax.set_position([0, 0, 1, 1])  # Adjust position and size
    ax.set_rlabel_position(1)

    # Add scale from 0 to 100 along the radius
    r_ticks = np.linspace(0, 1, 6)
    r_labels = [f"{int(t*100)}" for t in r_ticks]
    ax.set_yticks(r_ticks)
    ax.set_yticklabels(r_labels, color="gray", fontsize=8)

    c = ax.pcolormesh(hues * 2 * np.pi, saturations, rgb_values)

    # Remove labels and gridlines from axes
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(False)

    # Function to delete the temporary file when closing the program
    def delete_temporary_file(file_path):
        os.unlink(file_path)

    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        image_path = temp_file.name

    # Save the generated graph as an image file
    image_path = "color_wheel.png"
    plt.savefig(image_path, dpi=100, bbox_inches="tight", pad_inches=0)
    plt.close()

    # Register the function to delete the temporary file when the program closes
    atexit.register(delete_temporary_file, image_path)

    return image_path


def main():
    # Create the main window
    root = tk.Tk()
    root.title("LAB Color Chart")

    # Define the window icon
    #root.iconbitmap("C:/Users/arlie/OneDrive/CIELAB/TESTE/CIELAB.ico")

    # Label for instruction
    version_label = tk.Label(root, text="Enter the values of L*a*b*:", font=("Arial Bold", 9))
    version_label.pack(expand=True)

    # Define the window dimensions
    window_width = 400
    window_height = 200

    # Get the dimensions of the screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate the center position of the window
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2

    # Define the window geometry
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    def add():
        try:
            L_values = float(L_entry.get())
            a_values = float(a_entry.get())
            b_values = float(b_entry.get())

            points.append((L_values, a_values, b_values))

            # Generates the color wheel
            image_path = generate_color_wheel()

            # Create a list of all points, including existing points and the new point
            all_L_values = [point[0] for point in points]
            all_a_values = [point[1] for point in points]
            all_b_values = [point[2] for point in points]

            # Display the LAB color chart using the generated color wheel
            create_lab_color_chart(all_L_values, all_a_values, all_b_values, image_path)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid values for L*a*b*.")

    def clean_entries():
        L_entry.delete(0, "end")
        a_entry.delete(0, "end")
        b_entry.delete(0, "end")
        points.clear()  # Clears the list of points

    # List to store points
    points = []

    # Create the frame for the LAB values
    lab_frame = tk.Frame(root)
    lab_frame.pack(pady=10)

    # Create input fields for LAB values
    tk.Label(lab_frame, text="L*").grid(row=0, column=0)
    L_entry = tk.Entry(lab_frame)
    L_entry.grid(row=0, column=1)

    tk.Label(lab_frame, text="a*").grid(row=1, column=0)
    a_entry = tk.Entry(lab_frame)
    a_entry.grid(row=1, column=1)

    tk.Label(lab_frame, text="b*").grid(row=2, column=0)
    b_entry = tk.Entry(lab_frame)
    b_entry.grid(row=2, column=1)

    # Frame to contain the buttons
    button_frame = tk.Frame(root)
    button_frame.pack()

    # Button to add point and open new chart
    add_new_button = tk.Button(button_frame, text="Show/Insert", command=add)
    add_new_button.pack(side=tk.LEFT, padx=5)

    # Button to clear entries
    clear_entries_button = tk.Button(button_frame, text="Clear", command=clean_entries)
    clear_entries_button.pack(side=tk.LEFT, padx=5)

    # Button to exit
    def close_program():
        root.quit()
        root.destroy()
        for fig in figures:
            plt.close(fig)  # Closes all plot figures

    exit_button = tk.Button(button_frame, text="Exit", command=close_program)
    exit_button.pack(side=tk.LEFT, padx=5)

    version_label = tk.Label(root, text="2024 © LAB Color Chart v.1.1", font=("Arial Bold", 8))
    version_label.pack(expand=True)

    root.mainloop()


if __name__ == "__main__":
    # List to store plot figures
    figures = []
    main()
