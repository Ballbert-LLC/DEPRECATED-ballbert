import os
import fnmatch
import codecs
from collections import Counter

# count the total number of lines in all files in the directory and its subdirectories, grouped by file extension and sorted by number of lines


def count_lines_by_extension_and_directory_sorted(directory):
    lines_by_extension = {}
    lines_by_directory = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if fnmatch.fnmatch(file, '*'):  # count all files
                file_path = os.path.join(root, file)
                try:
                    with codecs.open(file_path, 'r', encoding='utf-8') as f:
                        num_lines = sum(1 for line in f)
                        extension = os.path.splitext(file)[1].lower()
                        if extension in lines_by_extension:
                            lines_by_extension[extension] += num_lines
                        else:
                            lines_by_extension[extension] = num_lines
                except UnicodeDecodeError:
                    pass  # ignore files with non-UTF-8 encoding

        for dir in dirs:
            dir_path = os.path.join(root, dir)
            level1_dir = os.path.basename(os.path.normpath(root))
            if level1_dir in lines_by_directory:
                lines_by_directory[level1_dir] += count_lines_in_directory(
                    dir_path)
            else:
                lines_by_directory[level1_dir] = count_lines_in_directory(
                    dir_path)

    lines_by_extension_sorted = sorted(
        lines_by_extension.items(), key=lambda x: x[1], reverse=True)
    lines_by_directory_sorted = Counter(lines_by_directory).most_common()

    return lines_by_extension_sorted, lines_by_directory_sorted

# count the total number of lines in a directory and its subdirectories


def count_lines_in_directory(directory):
    total_lines = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if fnmatch.fnmatch(file, '*'):  # count all files
                file_path = os.path.join(root, file)
                try:
                    with codecs.open(file_path, 'r', encoding='utf-8') as f:
                        num_lines = sum(1 for line in f)
                        total_lines += num_lines
                except UnicodeDecodeError:
                    pass  # ignore files with non-UTF-8 encoding
    return total_lines


# Usage:
extension_count, directory_count = count_lines_by_extension_and_directory_sorted(
    './')
print("Total number of lines by file extension:")
for extension, num_lines in extension_count:
    print(f"  {extension}: {num_lines}")

print("\nMost common first level directories by total number of lines:")
for directory, num_lines in directory_count:
    print(f"  {directory}: {num_lines}")
