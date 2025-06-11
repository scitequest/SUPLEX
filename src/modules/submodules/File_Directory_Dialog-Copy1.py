import os
from ipyfilechooser import FileChooser
import ipywidgets as widgets
from IPython.display import display, clear_output
from ipywidgets import VBox


def saveFileDialog():
    # Create a file chooser widget for saving a file
    file_chooser = FileChooser(use_dir_icons=True, show_hidden=False)
    file_chooser.show_only_dirs = False
    file_chooser.title = "<b>Select location and enter file name:</b>"
    file_chooser.default_filename = "new_file"

    # Create a dropdown for file format selection
    file_format_dropdown = widgets.Dropdown(
        options=[".txt", ".csv", ".json"],  # Add more formats as needed
        value=".txt",
        description="File Format:",
        style={"description_width": "initial"},
    )

    # Output widget for displaying status messages
    output = widgets.Output()

    # Function to handle the selection of a file
    def on_save_button_clicked(chooser):
        with output:
            output.clear_output()
            if file_chooser.selected:
                # Get the file path and append the selected file format
                file_path = file_chooser.selected
                selected_format = file_format_dropdown.value

                # Ensure file path has correct extension
                if not file_path.endswith(selected_format):
                    file_path += selected_format

                # Implement the logic to save your file
                try:
                    with open(file_path, "w") as f:
                        f.write("Sample content")
                    print(f"File '{file_path}' has been saved successfully.")
                except Exception as e:
                    print(f"Error saving file: {e}")
            else:
                print("No file selected.")

    # Attach the event handler
    file_chooser.register_callback(on_save_button_clicked)

    # Display the widgets
    display(VBox([file_chooser, file_format_dropdown, output]))


def loadFileDialog():
    # Create a file chooser widget for loading a file
    file_chooser = FileChooser(use_dir_icons=True, show_hidden=False)
    file_chooser.show_only_dirs = False
    file_chooser.title = "<b>Select a file to load:</b>"

    # Output widget for displaying status messages
    output = widgets.Output()

    # Function to handle the selection of a file
    def on_load_button_clicked(chooser):
        with output:
            output.clear_output()
            if file_chooser.selected:
                file_path = file_chooser.selected
                # Implement the logic to load your file
                try:
                    with open(file_path, "r") as f:
                        content = f.read()
                    print(f"File '{file_path}' has been loaded successfully.")
                    print("Content:")
                    print(content)
                except Exception as e:
                    print(f"Error loading file: {e}")
            else:
                print("No file selected.")

    # Attach the event handler
    file_chooser.register_callback(on_load_button_clicked)

    # Display the file chooser widget
    display(VBox([file_chooser, output]))


def loadDirectoryDialog():
    # Create a file chooser widget for loading a directory
    dir_chooser = FileChooser(use_dir_icons=True, show_hidden=False)
    dir_chooser.show_only_dirs = True
    dir_chooser.title = "<b>Select a directory to load:</b>"

    # Output widget for displaying status messages
    output = widgets.Output()

    # Function to handle the selection of a directory
    def on_load_dir_button_clicked(chooser):
        with output:
            output.clear_output()
            if dir_chooser.selected_path:
                directory_path = dir_chooser.selected_path
                print(f"Directory '{directory_path}' has been selected.")
                # Implement the logic to load your directory
                try:
                    files = os.listdir(directory_path)
                    print(f"Files in '{directory_path}':")
                    for file in files:
                        print(file)
                except Exception as e:
                    print(f"Error loading directory: {e}")
            else:
                print("No directory selected.")

    # Attach the event handler
    dir_chooser.register_callback(on_load_dir_button_clicked)

    # Display the directory chooser widget
    display(VBox([dir_chooser, output]))
