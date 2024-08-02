import os
import subprocess

# Open a file using the default application
def open_file(file_name):
    try:
        files = search_files(file_name)
        if files:
            for file in files:
                os.startfile(file)
            return f"Opening {len(files)} file(s) matching: {file_name}"
        else:
            return "File not found."
    except Exception as e:
        return f"Error opening file: {str(e)}"

def open_folder(folder_name):
    try:
        folders = search_folders(folder_name)
        if folders:
            for folder in folders:
                os.startfile(folder)
            return f"Opening {len(folders)} folder(s) matching: {folder_name}"
        else:
            return "Folder not found."
    except Exception as e:
        return f"Error opening folder: {str(e)}"

# Create an empty file
def create_file(file_path):
    try:
        with open(file_path, 'w') as f:
            pass
        return f"File created: {file_path}"
    except Exception as e:
        return f"Error creating file: {str(e)}"

# Delete a file
def delete_file(file_path):
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            return f"File deleted: {file_path}"
        else:
            return "File not found."
    except Exception as e:
        return f"Error deleting file: {str(e)}"

# Create a folder
def create_folder(folder_path):
    try:
        os.makedirs(folder_path, exist_ok=True)
        return f"Folder created: {folder_path}"
    except Exception as e:
        return f"Error creating folder: {str(e)}"

# Delete a folder
def delete_folder(folder_path):
    try:
        if os.path.isdir(folder_path):
            os.rmdir(folder_path)
            return f"Folder deleted: {folder_path}"
        else:
            return "Folder not found."
    except Exception as e:
        return f"Error deleting folder: {str(e)}"

# Searches files  
def search_files(search_term, base_path="."):
    matches = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if search_term.lower() in file.lower():
                matches.append(os.path.join(root, file))
    return matches

# Searches folders
def search_folders(search_term, base_path="."):
    matches = []
    for root, dirs, files in os.walk(base_path):
        for dir in dirs:
            if search_term.lower() in dir.lower():
                matches.append(os.path.join(root, dir))
    return matches


if __name__ == "__main__":
    # Example usage
    # create_folder('test_folder')
    # create_file('test_folder/testing.txt')
    
    # Open all files and folders matching the search term
    # file_matches = search_files('testing.txt')
    folder_matches = search_folders('m1n9')
    
    # open_file('testing.txt')
    open_folder('m1n9')
    
    # print(f"Files found: {file_matches}")
    print(f"Folders found: {folder_matches}")
