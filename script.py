import os
from github import Github
from ruamel.yaml import YAML

# Authentication
token = os.environ.get('GITHUB_TOKEN')
g = Github(token)

# Repository details
repo_name = "kb1110/Kubernetes"
repo = g.get_repo(repo_name)

# Create a new branch
base_branch = repo.get_branch("main")  # or "master", depending on your default branch name
new_branch_name = "update-resources"
repo.create_git_ref(ref=f"refs/heads/{new_branch_name}", sha=base_branch.commit.sha)

# Function to update file content
def update_file_content(file_path, new_cpu, new_memory):
    # Get the file content
    file = repo.get_contents(file_path, ref=new_branch_name)
    content = file.decoded_content.decode()

    # Parse YAML
    yaml = YAML()
    yaml.preserve_quotes = True
    data = yaml.load(content)

    # Update the resources section
    for container in data['spec']['template']['spec']['containers']:
        if 'resources' in container:
            if 'requests' not in container['resources']:
                container['resources']['requests'] = {}
            container['resources']['requests']['cpu'] = new_cpu
            container['resources']['requests']['memory'] = new_memory

    # Convert back to YAML
    new_content = yaml.dump(data)

    # Commit the change
    repo.update_file(
        file_path,
        f"Update resource requests in {file_path}",
        new_content,
        file.sha,
        branch=new_branch_name
    )

# Get user input
new_cpu = input("Enter new CPU request value (e.g., 1500m): ")
new_memory = input("Enter new Memory request value (e.g., 768Mi): ")

# Update files
files_to_update = ["details-v1.yaml"]
for file_path in files_to_update:
    update_file_content(file_path, new_cpu, new_memory)

# Create a pull request
pr = repo.create_pull(
    title="Update Resource Configuration",
    body=f"Automated update of resource configuration.\nNew CPU request: {new_cpu}\nNew Memory request: {new_memory}",
    head=new_branch_name,
    base="main"  # or "master", depending on your default branch name
)

print(f"Created PR: {pr.html_url}")