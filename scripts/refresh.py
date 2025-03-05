#!/usr/bin/python
import os
import subprocess
import shutil
from matrix_client.api import MatrixHttpApi

def run_command(command, cwd=None, env=None):
    """Run a shell command and return its output."""
    try:
        subprocess.run(command, cwd=cwd, check=True, timeout=60, env=env)
    except subprocess.TimeoutExpired as e:
        print(f"Process timed out.\n{e}")
        raise
    except subprocess.CalledProcessError as e:
        print(f"Process failed. Returned {e.returncode}\n{e}")
        raise


def git_command(repo_url, clone_dir, branch):
    """Clones or pulls a git repository."""
    try:
        if not os.path.isdir(os.path.join(clone_dir, '.git')):
            # Clone repository
            run_command(["git", "clone", "--depth", "1", "--branch", branch, repo_url, clone_dir])
        else:
            # Pull repository if already exists
            run_command(["git", "fetch", "-v"], cwd=clone_dir)
            run_command(["git", "reset", "--hard", f"origin/{branch}"], cwd=clone_dir)
    except Exception as e:
        print(f"Git operation failed: {str(e)}")
        raise

def send_matrix_message(message):
    matrix_server = os.getenv('MATRIX_SERVER', '')
    matrix_room = os.getenv('MATRIX_ROOM')
    matrix_token = os.getenv('MATRIX_TOKEN')
    if matrix_server != "" and matrix_room != "" and matrix_token != "":
        print(f"Sending message to {matrix_server} @ {matrix_room}")
        matrix = MatrixHttpApi(matrix_server, token=matrix_token)
        response = matrix.send_message(matrix_room, message)

def main():
    print("Building site..")

    # Environment variables (these should be set beforehand in your environment)
    transport = os.getenv('GIT_TRANSPORT', 'HTTP')
    git_http_insecure = os.getenv('GIT_HTTP_INSECURE', 'FALSE')
    git_repo_url = os.getenv('GIT_REPO_URL')
    git_clone_dest = os.getenv('GIT_CLONE_DEST')
    git_repo_branch = os.getenv('GIT_REPO_BRANCH', 'main')
    git_provider = os.getenv('GIT_PROVIDER')
    git_ssh_id_file = os.getenv('GIT_SSH_ID_FILE')
    git_repo_content_path = os.getenv('GIT_REPO_CONTENT_PATH')
    git_preserve_src = os.getenv('GIT_PRESERVE_SRC', 'FALSE')

    target_dir = os.getenv('TARGET_DIR')
    target_base_url = os.getenv('TARGET_BASE_URL')
    target_server_uri = os.getenv('TARGET_SERVER_URI')
    build_params = os.getenv('BUILD_PARAMS', '')
    project_type = os.getenv('PROJECT_TYPE', 'hugo')

    home = os.getenv('HOME', '/home/app')

    ## GIT_MANY_BRANCHES is used to define if we deploy one (prod) or many (devs) branches
    git_many_branches = os.getenv('GIT_MANY_BRANCHES', 'FALSE')

    # Determine schema
    schema = "http" if git_http_insecure == "TRUE" else "https"

    # Get the directory of the git clone destination
    clone_dir = os.path.basename(git_clone_dest)
    print(f"Working directory: {clone_dir}")

    # Handle cloning or pulling the repository based on transport method
    if transport == "SSH":
        print("Cloning/updating with SSH..")
        run_command(
            ["git", "clone", git_repo_url, clone_dir],
            env={"GIT_SSH_COMMAND": f"ssh -oStrictHostKeyChecking=no -i {git_ssh_id_file}"}
        )
    elif transport == "HTTP":
        if git_provider in ("GITHUB", "GITEA", "GITLAB"):
            print("Cloning/updating a private repo..")
            repo_url = f"{schema}://{git_repo_url}"
            # Use credentials from $HOME/.git-credentials
            run_command(["git", "config", "--global", "credential.helper", "store"])

            if shutil.which(f"{home}/git-credentials"):
                shutil.copy2( f"{home}/git-credentials",  f"{home}/.git-credentials")
        else:
            print("Cloning/updating a public repo..")
            repo_url = f"{schema}://{git_repo_url}"

        git_command(repo_url, clone_dir, git_repo_branch)
    else:
        print("Unsupported transport!")
        exit(-1)

    public_uri = f"{target_server_uri}{target_base_url}/{git_repo_branch}" if git_many_branches == "TRUE" else f"{target_server_uri}{target_base_url}"
    if project_type == "hugo":
        # Build the site using Hugo
        site_dir = f"{target_dir}/{git_repo_branch}" if git_many_branches == "TRUE" else target_dir
        os.makedirs(site_dir, exist_ok=True)

        hugo_cmd = ["hugo", "--destination", site_dir, "--baseURL", public_uri]
        if len(build_params) > 0:
            hugo_cmd += build_params.split(' ')

        run_command(hugo_cmd, cwd=os.path.join(clone_dir, git_repo_content_path))
        send_matrix_message(f"Site Update {public_uri}")
    elif project_type == "mkdocs":
        # Build the site using mkdocs
        site_dir = f"{target_dir}/{git_repo_branch}" if git_many_branches == "TRUE" else target_dir
        os.makedirs(site_dir, exist_ok=True)

        mkdocs_cmd = ["mkdocs", "build", "--site-dir", site_dir]
        if len(build_params) > 0:
            mkdocs_cmd += build_params.split(' ')

        run_command(mkdocs_cmd, cwd=os.path.join(clone_dir, git_repo_content_path))
        send_matrix_message(f"Site Update {public_uri}")
    else:
        print("Unsupported project type!")
        exit(-2)

    # Clean up the source directory if required
    if git_preserve_src == "FALSE":
        shutil.rmtree(clone_dir)


if __name__ == "__main__":
    main()
