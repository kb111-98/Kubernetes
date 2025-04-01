# import os
# from github import Github
# from ruamel.yaml import YAML

# # Authentication
# token = os.environ.get('GITHUB_TOKEN')
# g = Github(token)

# # Repository details
# repo_name = "kb111-98/Kubernetes"
# repo = g.get_repo(repo_name)

# # Create a new branch
# base_branch = repo.get_branch("main")  # or "master", depending on your default branch name
# new_branch_name = "update-resources"
# repo.create_git_ref(ref=f"refs/heads/{new_branch_name}", sha=base_branch.commit.sha)

# # Function to update file content
# def update_file_content(file_path, new_cpu, new_memory):
#     # Get the file content
#     file = repo.get_contents(file_path, ref=new_branch_name)
#     content = file.decoded_content.decode()

#     # Parse YAML
#     yaml = YAML()
#     yaml.preserve_quotes = True
#     data = yaml.load(content)

#     # Update the resources section
#     for container in data['spec']['template']['spec']['containers']:
#         if 'resources' in container:
#             if 'requests' not in container['resources']:
#                 container['resources']['requests'] = {}
#             container['resources']['requests']['cpu'] = new_cpu
#             container['resources']['requests']['memory'] = new_memory

#     # Convert back to YAML
#     new_content = yaml.dump(data)

#     # Commit the change
#     repo.update_file(
#         file_path,
#         f"Update resource requests in {file_path}",
#         new_content,
#         file.sha,
#         branch=new_branch_name
#     )

# # Get user input
# new_cpu = input("Enter new CPU request value (e.g., 1500m): ")
# new_memory = input("Enter new Memory request value (e.g., 768Mi): ")

# # Update files
# files_to_update = ["details-v1.yaml"]
# for file_path in files_to_update:
#     update_file_content(file_path, new_cpu, new_memory)

# # Create a pull request
# pr = repo.create_pull(
#     title="Update Resource Configuration",
#     body=f"Automated update of resource configuration.\nNew CPU request: {new_cpu}\nNew Memory request: {new_memory}",
#     head=new_branch_name,
#     base="main"  # or "master", depending on your default branch name
# )

# print(f"Created PR: {pr.html_url}")


# import os
# from github import Github, GithubException
# from ruamel.yaml import YAML
# from io import StringIO

# def create_automated_pr(repo_name, new_cpu, new_memory):
#     """
#     Creates a PR with updated resource requests for all deployment manifests in a repository
    
#     Args:
#         repo_name: GitHub repository name in format 'owner/repo'
#         new_cpu: New CPU request value (e.g., '500m')
#         new_memory: New Memory request value (e.g., '512Mi')
#     """
#     # Authentication
#     token = os.environ.get('GITHUB_TOKEN')
#     if not token:
#         print("Error: GitHub token not found")
#         return False
    
#     g = Github(token)
    
#     try:
#         # Get repository
#         repo = g.get_repo(repo_name)
#         print(f"Accessing repository: {repo_name}")
        
#         # Get default branch
#         default_branch = repo.default_branch
#         base_branch = repo.get_branch(default_branch)
        
#         # Create a new branch
#         new_branch_name = f"update-resources-{os.urandom(4).hex()}"
#         try:
#             repo.create_git_ref(ref=f"refs/heads/{new_branch_name}", sha=base_branch.commit.sha)
#             print(f"Created branch: {new_branch_name}")
#         except GithubException as e:
#             print(f"Error creating branch: {e}")
#             return False
        
#         # Recursively find all YAML/YML files in the repository
#         deployment_files = find_deployment_files(repo, new_branch_name)
#         if not deployment_files:
#             print("No Kubernetes deployment manifests found")
#             return False
        
#         print(f"Found {len(deployment_files)} deployment files to analyze")
        
#         # Update deployment files with resources
#         updated_files = []
#         for file_path in deployment_files:
#             if update_file_resources(repo, file_path, new_branch_name, new_cpu, new_memory):
#                 updated_files.append(file_path)
        
#         if not updated_files:
#             print("No files were updated")
#             return False
        
#         # Create a pull request
#         pr = repo.create_pull(
#             title="Update Resource Configuration",
#             body=f"Automated update of resource configuration for {len(updated_files)} deployment(s).\n\n"
#                  f"New CPU request: {new_cpu}\n"
#                  f"New Memory request: {new_memory}\n\n"
#                  f"Updated files:\n- " + "\n- ".join(updated_files),
#             head=new_branch_name,
#             base=default_branch
#         )
        
#         print(f"Created PR: {pr.html_url}")
#         return True
        
#     except GithubException as e:
#         print(f"GitHub API error: {e}")
#         return False

# def find_deployment_files(repo, branch_name, path=''):
#     """Recursively find all Kubernetes deployment manifests in the repository"""
#     deployment_files = []
    
#     try:
#         contents = repo.get_contents(path, ref=branch_name)
        
#         for content in contents:
#             if content.type == "dir":
#                 # Recursively check subdirectories
#                 deployment_files.extend(find_deployment_files(repo, branch_name, content.path))
#             elif content.name.endswith(('.yaml', '.yml')):
#                 # Check if it's a Kubernetes deployment
#                 try:
#                     file_content = content.decoded_content.decode()
#                     yaml = YAML()
#                     data = yaml.load(file_content)
                    
#                     if (isinstance(data, dict) and 
#                         data.get('kind') == 'Deployment' and 
#                         'apiVersion' in data and 
#                         'spec' in data):
                        
#                         # Check if it has containers with resources
#                         containers = data.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
#                         if containers:
#                             deployment_files.append(content.path)
#                 except Exception:
#                     # Skip files that can't be parsed as YAML
#                     pass
#     except GithubException:
#         # Handle API errors or empty directories
#         pass
    
#     return deployment_files

# def update_file_resources(repo, file_path, branch_name, new_cpu, new_memory):
#     """Update resource requests in a deployment file"""
#     try:
#         file = repo.get_contents(file_path, ref=branch_name)
#         content = file.decoded_content.decode()
        
#         yaml = YAML()
#         yaml.preserve_quotes = True
#         data = yaml.load(content)
        
#         # Track if we made any changes
#         changes_made = False
        
#         # Update container resources
#         containers = data.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
#         for container in containers:
#             if 'resources' not in container:
#                 container['resources'] = {}
                
#             if 'requests' not in container['resources']:
#                 container['resources']['requests'] = {}
                
#             # Only update if values are different
#             current_cpu = container['resources']['requests'].get('cpu')
#             current_memory = container['resources']['requests'].get('memory')
            
#             if current_cpu != new_cpu or current_memory != new_memory:
#                 container['resources']['requests']['cpu'] = new_cpu
#                 container['resources']['requests']['memory'] = new_memory
#                 changes_made = True
        
#         if changes_made:
#             # Convert back to YAML
#             stream = StringIO()
#             yaml.dump(data, stream)
#             new_content = stream.getvalue()
            
#             # Commit changes
#             repo.update_file(
#                 file_path,
#                 f"Update resource requests in {file_path}",
#                 new_content,
#                 file.sha,
#                 branch=branch_name
#             )
#             print(f"Updated {file_path}")
#             return True
#         else:
#             print(f"No changes needed for {file_path}")
#             return False
        
#     except Exception as e:
#         print(f"Error updating {file_path}: {e}")
#         return False

# # Example usage 
# if __name__ == "__main__":
#     repo_name = input("Enter GitHub repository name (owner/repo): ")
#     new_cpu = input("Enter new CPU request value (e.g., 500m): ")
#     new_memory = input("Enter new Memory request value (e.g., 512Mi): ")
    
#     if create_automated_pr(repo_name, new_cpu, new_memory):
#         print("PR created successfully")
#     else:
#         print("Failed to create PR")





import os
from github import Github, GithubException
from ruamel.yaml import YAML
from io import StringIO

def create_automated_pr(repo_name, deployment_name, container_name, new_cpu, new_memory):
    """
    Creates a PR with updated resource requests for a specific deployment
    
    Args:
        repo_name: GitHub repository name in format 'owner/repo'
        deployment_name: Name of the deployment to update
        new_cpu: New CPU request value (e.g., '500m')
        new_memory: New Memory request value (e.g., '512Mi')
    """
    # Authentication
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("Error: GitHub token not found")
        return False
    
    g = Github(token)
    
    try:
        # Get repository
        repo = g.get_repo(repo_name)
        print(f"Accessing repository: {repo_name}")
        
        # Get default branch
        default_branch = repo.default_branch
        base_branch = repo.get_branch(default_branch)
        
        # Create a new branch
        new_branch_name = f"update-{deployment_name}-resources-{os.urandom(4).hex()}"
        try:
            repo.create_git_ref(ref=f"refs/heads/{new_branch_name}", sha=base_branch.commit.sha)
            print(f"Created branch: {new_branch_name}")
        except GithubException as e:
            print(f"Error creating branch: {e}")
            return False
        
        # Find deployment files for the specific deployment
        deployment_files = find_deployment_files(repo, new_branch_name, deployment_name)
        if not deployment_files:
            print(f"No deployment files found for {deployment_name}")
            return False
        
        print(f"Found {len(deployment_files)} deployment files to update")
        
        # Update deployment files with resources
        updated_files = []
        for file_path in deployment_files:
            if update_file_resources(repo, file_path, new_branch_name,container_name, new_cpu, new_memory):
                updated_files.append(file_path)
        
        if not updated_files:
            print("No files were updated")
            return False
        
        # Create a pull request
        pr = repo.create_pull(
            title=f"Update Resource Configuration for {deployment_name}",
            body=f"Automated update of resource configuration for deployment: {deployment_name}.\n\n"
                 f"New CPU request: {new_cpu}\n"
                 f"New Memory request: {new_memory}\n\n"
                 f"Updated files:\n- " + "\n- ".join(updated_files),
            head=new_branch_name,
            base=default_branch
        )
        
        print(f"Created PR: {pr.html_url}")
        return True
        
    except GithubException as e:
        print(f"GitHub API error: {e}")
        return False

def find_deployment_files(repo, branch_name, deployment_name, path=''):
    """
    Recursively find Kubernetes deployment manifests for a specific deployment name
    
    Args:
        repo: GitHub repository object
        branch_name: Branch to search in
        deployment_name: Name of the specific deployment to find
        path: Current path being searched (for recursive calls)
    
    Returns:
        List of file paths for matching deployment manifests
    """
    deployment_files = []
    
    try:
        contents = repo.get_contents(path, ref=branch_name)
        
        for content in contents:
            if content.type == "dir":
                # Recursively check subdirectories
                deployment_files.extend(find_deployment_files(repo, branch_name, deployment_name, content.path))
            elif content.name.endswith(('.yaml', '.yml')):
                # Check if it's a Kubernetes deployment
                try:
                    file_content = content.decoded_content.decode()
                    yaml = YAML()
                    data = yaml.load(file_content)
                    
                    if (isinstance(data, dict) and 
                        data.get('kind') == 'Deployment' and 
                        'apiVersion' in data and 
                        'spec' in data):
                        
                        # Check if deployment name matches
                        manifest_deployment_name = data.get('metadata', {}).get('name')
                        
                        if manifest_deployment_name == deployment_name:
                            # Check if it has containers with resources
                            containers = data.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
                            if containers:
                                deployment_files.append(content.path)
                except Exception:
                    # Skip files that can't be parsed as YAML
                    pass
    except GithubException:
        # Handle API errors or empty directories
        pass
    
    return deployment_files

def update_file_resources(repo, file_path, branch_name, container_name, new_cpu, new_memory):
    """Update resource requests in a deployment file"""
    try:
        file = repo.get_contents(file_path, ref=branch_name)
        content = file.decoded_content.decode()
        
        yaml = YAML()
        yaml.preserve_quotes = True
        data = yaml.load(content)
        
        # Track if we made any changes
        changes_made = False
        
        # Update container resources
        containers = data.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
        for container in containers:
            # Only update the specified container
            if container.get('name') == container_name:
                if 'resources' not in container:
                    container['resources'] = {}
                    
                if 'requests' not in container['resources']:
                    container['resources']['requests'] = {}
                    
                # Only update if values are different
                current_cpu = container['resources']['requests'].get('cpu')
                current_memory = container['resources']['requests'].get('memory')
                
                if current_cpu != new_cpu or current_memory != new_memory:
                    container['resources']['requests']['cpu'] = new_cpu
                    container['resources']['requests']['memory'] = new_memory
                    changes_made = True
    
        
        if changes_made:
            # Convert back to YAML
            stream = StringIO()
            yaml.dump(data, stream)
            new_content = stream.getvalue()
            
            # Commit changes
            repo.update_file(
                file_path,
                f"Update resource requests in {file_path}",
                new_content,
                file.sha,
                branch=branch_name
            )
            print(f"Updated {file_path}")
            return True
        else:
            print(f"No changes needed for {file_path}")
            return False
        
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

# Example usage 
if __name__ == "__main__":
    repo_name = input("Enter GitHub repository name (owner/repo): ")
    deployment_name = input("Enter deployment name to update: ")
    container_name = input("Enter container name to update: ")
    new_cpu = input("Enter new CPU request value (e.g., 500m): ")
    new_memory = input("Enter new Memory request value (e.g., 512Mi): ")
    
    if create_automated_pr(repo_name, deployment_name, container_name, new_cpu, new_memory):
        print("PR created successfully")
    else:
        print("Failed to create PR")