import os
import ast
import pkg_resources


def is_valid_package_name(package_name):
    # Filter out invalid package names (customize as needed)
    return not package_name.startswith("_") and package_name.isidentifier()


def find_required_packages(directory):
    required_packages = set()

    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".py"):
                filepath = os.path.join(root, filename)
                with open(filepath, "r", encoding="utf-8") as file:
                    try:
                        tree = ast.parse(file.read())
                    except SyntaxError:
                        # Skip files with syntax errors
                        continue

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            package_name = alias.name.split(".")[0]
                            if is_valid_package_name(package_name):
                                required_packages.add(package_name)
                    elif isinstance(node, ast.ImportFrom) and node.module is not None:
                        package_name = node.module.split(".")[0]
                        if is_valid_package_name(package_name):
                            required_packages.add(package_name)

    return required_packages


def write_requirements_txt(directory, output_file="requirements.txt"):
    required_packages = find_required_packages(directory)

    with open(output_file, "w", encoding="utf-8") as req_file:
        for package in sorted(required_packages):
            try:
                distribution = pkg_resources.get_distribution(package)
                req_file.write(f"{distribution.project_name}=={distribution.version}\n")
            except pkg_resources.DistributionNotFound:
                # Package not found in the current environment, write only package name
                req_file.write(f"{package}\n")


if __name__ == "__main__":
    project_directory = "./"
    write_requirements_txt(project_directory)
