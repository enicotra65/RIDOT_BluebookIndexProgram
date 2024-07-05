# RIDOT_BluebookIndexProgram
This program makes accessing any of the information from any of the versions of the RIDOT Bluebook easily accessible.

In order to run the web application you must follow these steps:

1. Ensure you have the latest version of python installed on your local machine:
	- To do this open your command line and type "python --version"
	- If it returns a version number, move on to step 2, otherwise go to the python website and ensure your local machine has python properly installed

2. Ensure you have the latest version of Flask installed:
	- To see if you have flask installed in enter these commands:
		>>>"python"
		>>>"import flask"
		>>>"flask.__version"

	- If the Command Line returns a version number, you HAVE Flask and CAN move on to step 3.

	- If the Command Line returns an error you will need to go to the flask website and follow the steps to properly install Flask on your local machine.
		- This command should install Flask properly: "pip install Flask"

3. Launch the app.py script in command line:
	- If your using a windows operating system:
		- (First ensure that you are in the same directory that the Program Folder is in, in your Terminal.)
		- Open Command Line: type 
			- "cd RIDOT_BluebookIndexProgram"
		- Once in the programs directory, to run the application type: 
			- "py app.py"
		- The web server should return a clickable link to open the front-end GUI of the application
			- Once the Program has loaded on the webpage, the program should be fully operational to use!	

4. If the program is throwing errors you may also need to install these dependencies for it to function properly:
	- in the command line enter:
		- "pip install PyMuPDF"
		 

