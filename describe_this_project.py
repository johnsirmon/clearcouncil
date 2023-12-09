
import os

def count_files(folder_path):
    file_count = 0
    file_types = {}

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_count += 1
            file_extension = os.path.splitext(file)[1]
            file_types[file_extension] = file_types.get(file_extension, 0) + 1

    return file_count, file_types

project_path = "/c:/Source/clearcouncil/describe_this_project.py"
total_files, folder_files = count_files(project_path)

print("Folder Structure:")
for root, dirs, files in os.walk(project_path):
    level = root.replace(project_path, '').count(os.sep)
    indent = ' ' * 4 * (level)
    print('{}{}/'.format(indent, os.path.basename(root)))

    for file_extension, count in folder_files.items():
        print('{}{}: {}'.format(indent, file_extension, count))

print("Total Files:", total_files)

import os

