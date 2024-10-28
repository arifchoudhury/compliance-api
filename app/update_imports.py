import os
import re

def update_imports(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()

                # Regular expression to find the target import statements
                updated_content = re.sub(
                    r'from compliance_lib_schemas.serializers import (.+)',
                    r'from compliance_lib_schemas.serializers import \1',
                    content
                )

                if updated_content != content:
                    with open(file_path, 'w') as f:
                        f.write(updated_content)
                    print(f'Updated imports in {file_path}')

if __name__ == "__main__":
    project_directory = '/Users/arif/Documents/business/project-bala/compliance-api/app'  # Update this path to your project directory
    update_imports(project_directory)
