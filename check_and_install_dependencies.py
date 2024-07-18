import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_and_install_dependencies():
    try:
        import flask
    except ImportError:
        print("Flask is not installed. Installing Flask...")
        install("Flask==2.3.2")
    
    try:
        import fitz
    except ImportError:
        print("PyMuPDF is not installed. Installing PyMuPDF...")
        install("PyMuPDF==1.19.6")

if __name__ == "__main__":
    check_and_install_dependencies()