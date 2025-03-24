import os
import shutil

def flatten_and_move_files(source_dir, destination_dir):
    """
    Recursively traverse source_dir, flatten the file structure, 
    and move files to destination_dir with new names.
    """
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    for root, _, files in os.walk(source_dir):
        for file in files:
            # Get the relative path and replace directory separators with "-"
            relative_path = os.path.relpath(root, source_dir)
            if relative_path == ".":
                relative_path = ""
            flattened_name = f"{relative_path.replace(os.sep, '-')}-{file}" if relative_path else file

            # Define source and destination file paths
            source_file = os.path.join(root, file)
            destination_file = os.path.join(destination_dir, flattened_name)

            # Move the file
            shutil.move(source_file, destination_file)
            print(f"Moved: {source_file} -> {destination_file}")

# Example usage:
source_directory = "msrcorid"  # Change to your source folder path
destination_directory = "dataset"  # Change to your destination folder path

flatten_and_move_files(source_directory, destination_directory)

def rename_files_in_folder(folder_path, replace_from=" ", replace_with="-"):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            old_path = os.path.join(root, file)
            new_name = file.replace(replace_from, replace_with)
            new_path = os.path.join(root, new_name)

            if old_path != new_path:  # Only rename if different
                os.rename(old_path, new_path)
                print(f'Renamed: {old_path} -> {new_path}')

# Example usage:
rename_files_in_folder("dataset")
