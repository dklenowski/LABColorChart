import numpy as np
import PySimpleGUI as sg
import os
import colorsys
import matplotlib.pyplot as plt
import tempfile
import atexit


def create_lab_color_chart(L_values, a_values, b_values, image_path):
    def close_event(event):
        # Clears data when plot window is closed
        L_values.clear()
        a_values.clear()
        b_values.clear()

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
            color=["none" if x >= 0 and y >= 0 else "none" for x, y in zip(a_values, b_values)],
            edgecolors="black",
            linewidths=1.5,
        )

        # Note points on the graph
        for a, b in zip(a_values, b_values):
            ax.annotate(f"({a};{b})", (a, b), textcoords="offset points", xytext=(0, 5), ha="center", va="bottom")

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
        point = L_values
        normalized_point = point
        cb.ax.plot(
            [0, 1],
            [normalized_point, normalized_point],
            color="red",
            linewidth=5,
            marker="_",
            markersize=8,
            label="Manual Point",
        )

        # Add plot window close event
        fig.canvas.mpl_connect("close_event", close_event)

        # Display the graph
        plt.show()

    except Exception as e:
        sg.popup_error(f"Error displaying chart: {str(e)}")


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

    # Register the function to delete the temporary file upon program termination
    atexit.register(delete_temporary_file, image_path)

    return image_path


def main():
    sg.theme("DarkGrey11")

    # GUI layout
    layout = [
        [sg.Text("")],  # Blank line
        [sg.Text("Enter the values of L*a*b*:", size=(20, 1), justification="center")],
        [sg.Text("")],  # Blank line
        [sg.Text("L*:", size=(2, 1)), sg.InputText(key="L")],
        [sg.Text("a*:", size=(2, 1)), sg.InputText(key="a")],
        [sg.Text("b*:", size=(2, 1)), sg.InputText(key="b")],
        [sg.Text("")],  # Blank line
        [sg.Button("Show", size=(10, 1)), sg.Button("Clear", size=(10, 1)), sg.Button("Exit", size=(10, 1))],
        [sg.Text("")],  # Blank line
        [sg.Text("")],  # Blank line
        [sg.Text("2024 © LAB Color Chart v.1.2", size=(30, 1), font=("Arial Bold", 8), justification="center")],
    ]

    # Create the window with the icon
    window = sg.Window(
        "LAB Color Chart",
        layout,
        # icon="C:/Users/arlie/OneDrive/CIELAB/TESTE/CIELAB.ico",
        size=(500, 300),
        element_justification="center",
    )

    L_values = []
    a_values = []
    b_values = []

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "Exit":
            break

        if event == "Show":
            try:
                L_values.append(float(values["L"]))
                a_values.append(float(values["a"]))
                b_values.append(float(values["b"]))

                # Generates the color wheel
                image_path = generate_color_wheel()

                # Display the LAB color chart using the generated color wheel
                create_lab_color_chart(L_values, a_values, b_values, image_path)

            except ValueError:
                sg.popup_ok("Please enter valid values for L*a*b*.")

        if event == "Clear":
            # Clears the L*, a* and b* values
            window["L"].update("")
            window["a"].update("")
            window["b"].update("")
            L_values.clear()
            a_values.clear()
            b_values.clear()

    window.close()


if __name__ == "__main__":
    main()
