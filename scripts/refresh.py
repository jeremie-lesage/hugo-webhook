#!/usr/bin/python
import os
import subprocess
import shutil

def run_command(command, cwd=None):
    """Run a shell command and return its output."""
    result = None
    try:
        print(f"---\n> {command}")
        result = subprocess.run(command, shell=True, cwd=cwd, check=True, capture_output=True, timeout=60)
        print(result.stdout.decode('utf-8').strip())
        if result.stderr is not None:
            print(result.stderr.decode('utf-8').strip())
        print("-----")
        return result.stdout.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        if result is not None:
            if result.stdout is not None:
                print(result.stdout.decode('utf-8').strip())
                print("~~~~")
            if result.stderr is not None:
                print(result.stderr.decode('utf-8').strip())
                print("~~~~")

        if e.stderr is not None:
            print(f"Command '{command}' failed with error: {e.stderr.decode('utf-8').strip()}")
        else:
            print(f"Command '{command}' failed: {str(e)}")

        raise

def git_command(repo_url, clone_dir, branch):
    """Clones or pulls a git repository."""
    try:
        if not os.path.isdir(os.path.join(clone_dir, '.git')):
            # Clone repository
            run_command(f"git clone --depth 1 {repo_url} {clone_dir}")
        else:
            # Pull repository if already exists
            run_command(f"git pull --ff-only origin {branch}", cwd=clone_dir)
    except Exception as e:
        print(f"Git operation failed: {str(e)}")
        raise

def main():
    print("Building site..")

    # Environment variables (these should be set beforehand in your environment)
    TRANSPORT = os.getenv('GIT_TRANSPORT', 'HTTP')
    GIT_HTTP_INSECURE = os.getenv('GIT_HTTP_INSECURE', 'FALSE')
    GIT_REPO_URL = os.getenv('GIT_REPO_URL')
    GIT_CLONE_DEST = os.getenv('GIT_CLONE_DEST')
    GIT_REPO_BRANCH = os.getenv('GIT_REPO_BRANCH', 'main')
    GIT_TOKEN = os.getenv('GIT_TOKEN')
    GIT_USERNAME = os.getenv('GIT_USERNAME')
    GIT_PROVIDER = os.getenv('GIT_PROVIDER')
    GIT_SSH_ID_FILE = os.getenv('GIT_SSH_ID_FILE')
    GIT_REPO_CONTENT_PATH = os.getenv('GIT_REPO_CONTENT_PATH')
    TARGET_DIR = os.getenv('TARGET_DIR')
    HUGO_PARAMS = os.getenv('HUGO_PARAMS', '')
    MKDOCS_PARAMS = os.getenv('MKDOCS_PARAMS', '')
    GIT_PRESERVE_SRC = os.getenv('GIT_PRESERVE_SRC', 'FALSE')
    PROJECT_TYPE = os.getenv('PROJECT_TYPE', 'hugo')

    # Determine schema
    SCHEMA = "http" if GIT_HTTP_INSECURE == "TRUE" else "https"
    ERASE = 0

    # Get the directory of the git clone destination
    clone_dir = os.path.basename(GIT_CLONE_DEST)
    print(f"Working directory: {clone_dir}")
    #os.makedirs(clone_dir, exist_ok=True)

    # Handle cloning or pulling the repository based on transport method
    if TRANSPORT == "SSH":
        git_ssh_command = f"ssh -oStrictHostKeyChecking=no -i {GIT_SSH_ID_FILE}"
        run_command(f"GIT_SSH_COMMAND=\"{git_ssh_command}\" git clone {GIT_REPO_URL} {clone_dir}")
    elif TRANSPORT == "HTTP":
        if GIT_PROVIDER == "GITHUB":
            repo_url = f"{SCHEMA}://{GIT_TOKEN}:x-oauth-basic@{GIT_REPO_URL}"
        elif GIT_PROVIDER in ("GITEA", "GITLAB"):
            repo_url = f"{SCHEMA}://{GIT_USERNAME}:{GIT_TOKEN}@{GIT_REPO_URL}"
        else:
            print("Cloning/updating a public repo..")
            repo_url = f"{SCHEMA}://{GIT_REPO_URL}"

        git_command(repo_url, clone_dir, GIT_REPO_BRANCH)
    else:
        print("Unsupported transport!")
        exit(-1)

    if PROJECT_TYPE == "hugo":
        # Build the site using Hugo
        # os.makedirs(TARGET_DIR, exist_ok=True)
        hugo_command = f"hugo --destination {TARGET_DIR} {HUGO_PARAMS}"
        run_command(hugo_command, cwd=os.path.join(clone_dir, GIT_REPO_CONTENT_PATH))
    elif PROJECT_TYPE == "mkdocs":
        mkdocs_command = f"mkdocs build --site-dir {TARGET_DIR} {MKDOCS_PARAMS}"
        run_command(mkdocs_command, cwd=os.path.join(clone_dir, GIT_REPO_CONTENT_PATH))
    else:
        print("Unsupported project type!")
        exit(-2)


    # Clean up the source directory if required
    if GIT_PRESERVE_SRC == "FALSE":
        shutil.rmtree(clone_dir)

if __name__ == "__main__":
    main()
