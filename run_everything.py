import os
import subprocess
import sys

def main():
    print("Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("Running Data Pipeline...")
    subprocess.check_call([sys.executable, "data_pipeline.py"])
    
    print("Generating Visuals...")
    subprocess.check_call([sys.executable, "generate_visuals.py"])
    
    print("All done! Open kitoko_dashboard.html in your browser to see the new data and design.")

if __name__ == "__main__":
    main()
