import argparse
import sys
import shutil
import subprocess
import os

ISAACLAB_DIR = "/workspace/isaaclab"
source_dir = os.path.join(ISAACLAB_DIR, "source")
RESOURCES_DIR = os.path.join(source_dir, "hcrl_isaaclab", "resources")
hcrl_robots_dir = os.path.join(RESOURCES_DIR, "hcrl_robots")

parser = argparse.ArgumentParser()
parser.add_argument(
    "--job-script", type=str, default=f"{source_dir}/hcrl_isaaclab/scripts/train.py", help="Job script to run."
)
args, remaining_args = parser.parse_known_args()


if __name__ == "__main__":
    # copy all python_packages into the isaaclab source/ dir
    python_packages = [p for p in sys.path if "/py_modules_files/" in p]
    folder_names: list[str] = []
    for p in python_packages:
        shutil.copytree(p, source_dir, dirs_exist_ok=True)
        folder_names += os.listdir(p)

    # make symlink to hcrl_robots
    os.makedirs(RESOURCES_DIR, exist_ok=True)
    if os.path.exists(hcrl_robots_dir):
        os.remove(hcrl_robots_dir)
    os.symlink(os.path.join(ISAACLAB_DIR, "hcrl_robots"), os.path.join(RESOURCES_DIR, "hcrl_robots"))

    # install dependencies of new modules
    for name in folder_names:
        if os.path.exists(os.path.join(source_dir, name, "setup.py")):
            subprocess.run([sys.executable, "-m", "pip", "install", "--editable", os.path.join(source_dir, name)])

    # run train script
    print(f"Executing {sys.executable} on {args.job_script} with args {remaining_args}")
    subprocess.run([sys.executable, args.job_script, *remaining_args])

    # clean up symlink and copied directories
    os.remove(hcrl_robots_dir)
    for name in folder_names:
        folder = os.path.join(source_dir, name)
        if os.path.isdir(folder):
            shutil.rmtree(folder)
        else:
            os.remove(folder)
