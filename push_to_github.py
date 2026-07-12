import subprocess
import os
import sys

def run(cmd):
    print(f"Running: {cmd}")
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        print(output.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.output.decode('utf-8')}")

def main():
    run("git init")
    run("git add .")
    run('git commit -m "Initial commit of Kitoko RFM Analysis project"')
    run("git branch -M main")
    run("git remote add origin https://github.com/hemalsureja/Kitoko-RFM-Analysis.git")
    run("git push -u origin main")

if __name__ == "__main__":
    main()
