import os

from messenger import get_file_data


def get_or_create_file(working_dir, file_name):
    content = ""
    file_path = os.path.join(working_dir, file_name)
    if not os.path.exists(file_path):
        # Fetch the content from the specified URL
        content = get_file_data(file_name)
        # Create the file and write the content to it
        with open(file_path, "w") as file:
            file.write(content)
    else:
        # Read the content of the file
        with open(file_path, "r") as file:
            content = file.read()
    return content
