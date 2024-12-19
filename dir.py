import os

def generate_directory_structure(directory, output_file):
    """
    Generate a directory structure and save it to a .txt file.

    Args:
        directory (str): The root directory to analyze.
        output_file (str): The name of the file to save the structure to.
    """
    with open(output_file, 'w') as file:
        for root, dirs, files in os.walk(directory):
            level = root.replace(directory, "").count(os.sep)
            indent = " " * 4 * level
            file.write(f"{indent}{os.path.basename(root)}/\n")
            sub_indent = " " * 4 * (level + 1)
            for f in files:
                file.write(f"{sub_indent}{f}\n")

if __name__ == "__main__":
    # Root directory for the structure
    root_dir = os.path.abspath(".")  # Current directory

    # Output file to save the structure
    output_file_name = "directory_structure.txt"

    generate_directory_structure(root_dir, output_file_name)
    print(f"Directory structure saved to {output_file_name}")
