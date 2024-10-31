#!/usr/bin/python
import os
import subprocess
import shutil


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
            run_command(["git", "clone", "--depth", "1", repo_url, clone_dir])
        else:
            # Pull repository if already exists
            run_command(["git", "fetch", "-v"], cwd=clone_dir)
            run_command(["git", "reset", "--hard", f"origin/{branch}"], cwd=clone_dir)
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
    GIT_PROVIDER = os.getenv('GIT_PROVIDER')
    GIT_SSH_ID_FILE = os.getenv('GIT_SSH_ID_FILE')
    GIT_REPO_CONTENT_PATH = os.getenv('GIT_REPO_CONTENT_PATH')
    GIT_PRESERVE_SRC = os.getenv('GIT_PRESERVE_SRC', 'FALSE')

    TARGET_DIR = os.getenv('TARGET_DIR')
    TARGET_BASE_URL = os.getenv('TARGET_BASE_URL')
    BUILD_PARAMS = os.getenv('BUILD_PARAMS', '')
    PROJECT_TYPE = os.getenv('PROJECT_TYPE', 'hugo')

    ## GIT_MANY_BRANCHES is used to define if we deploy one (prod) or many (devs) branches
    GIT_MANY_BRANCHES = os.getenv('GIT_MANY_BRANCHES', 'FALSE')

    # Determine schema
    SCHEMA = "http" if GIT_HTTP_INSECURE == "TRUE" else "https"

    # Get the directory of the git clone destination
    clone_dir = os.path.basename(GIT_CLONE_DEST)
    print(f"Working directory: {clone_dir}")

    # Handle cloning or pulling the repository based on transport method
    if TRANSPORT == "SSH":
        print("Cloning/updating with SSH..")
        run_command(
            ["git", "clone", GIT_REPO_URL, clone_dir],
            env={"GIT_SSH_COMMAND": f"ssh -oStrictHostKeyChecking=no -i {GIT_SSH_ID_FILE}"}
        )
    elif TRANSPORT == "HTTP":
        if GIT_PROVIDER in ("GITHUB", "GITEA", "GITLAB"):
            print("Cloning/updating a private repo..")
            repo_url = f"{SCHEMA}://{GIT_REPO_URL}"
            # Use credentials from $HOME/.git-credentials
            run_command(["git", "config", "--global", "credential.helper", "store"])
        else:
            print("Cloning/updating a public repo..")
            repo_url = f"{SCHEMA}://{GIT_REPO_URL}"

        git_command(repo_url, clone_dir, GIT_REPO_BRANCH)
    else:
        print("Unsupported transport!")
        exit(-1)

    if PROJECT_TYPE == "hugo":
        # Build the site using Hugo
        site_dir = f"{TARGET_DIR}/{GIT_REPO_BRANCH}" if GIT_MANY_BRANCHES == "TRUE" else TARGET_DIR
        os.makedirs(site_dir, exist_ok=True)
        base_url = f"{TARGET_BASE_URL}/{GIT_REPO_BRANCH}" if GIT_MANY_BRANCHES == "TRUE" else TARGET_BASE_URL
        run_command(
            ["hugo", "--destination", site_dir, "--baseURL", base_url] + BUILD_PARAMS.split(' '),
            cwd=os.path.join(clone_dir, GIT_REPO_CONTENT_PATH)
        )
    elif PROJECT_TYPE == "mkdocs":
        # Build the site using mkdocs
        site_dir = f"{TARGET_DIR}/{GIT_REPO_BRANCH}" if GIT_MANY_BRANCHES == "TRUE" else TARGET_DIR
        os.makedirs(site_dir, exist_ok=True)
        run_command(
            ["mkdocs", "build", "--site-dir", site_dir] + BUILD_PARAMS.split(' '),
            cwd=os.path.join(clone_dir, GIT_REPO_CONTENT_PATH)
        )
    else:
        print("Unsupported project type!")
        exit(-2)

    # Clean up the source directory if required
    if GIT_PRESERVE_SRC == "FALSE":
        shutil.rmtree(clone_dir)


if __name__ == "__main__":
    main()
