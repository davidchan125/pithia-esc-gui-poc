# 🌍 PITHIA e-Science Centre
The code base for the PITHIA e-Science Centre Prototype.

## Set up the e-Science Centre prototype on your local machine
### Install Python
Instructions to install Python can be found under the **Install Python** section of the [Django quick install guide](https://docs.djangoproject.com/en/4.0/intro/install/).

### Set up a local MongoDB database
This project requires a MongoDB database to store e-Science Centre resources (e.g., Data Collection metadata). To set up a local database for development, please follow the [official Install MongoDB guide](https://www.mongodb.com/docs/guides/server/install/). When you are at the part of the guide where you are choosing the type of MongoDB deployment (i.e., when you are at the [MongoDB Download Center](https://www.mongodb.com/try)), select **On-premises**, then select and download the latest version of the **MongoDB Community Server**.

### Clone the GitHub repo
Assuming you have Git and a terminal application installed (if not, this page [here](https://git-scm.com/downloads) will provide a download link to install the Git Bash terminal and Git on your machine), from your terminal, navigate to the folder you would like to store the repository in (e.g., `cd ~/Documents/Projects`), then copy the clone link for this repository and run `git clone <the repo clone link>`, replacing `<the repo clone link>` with the clone link for this repository. This will download a copy of the project repository to your local machine.

### Create a Python virtual environment for the project
To create a virtual environment for the project, first, open up your terminal application and `cd` into the root of the project folder. Then, enter in one of the following lines, depending on your operating system, into your terminal:
- **MacOS/Linux**: `python3 -m venv venv`
- **Windows**: `py -m venv venv`

#### Activate the Python virtual environment
Enter one of the following lines, depending on your operating system, into your terminal to activate the virtual environment:
- **MacOS/Linux**: `source venv/bin/activate`
- **Windows**: `venv/Scripts/activate`

Entering `deactivate` into your terminal will deactivate the virtual environment, and entering one of the lines listed above in again will reactivate the virtual environment. You will need to activate the virtual environment everytime you want to run the project locally.

### Install the project's Python dependencies
Enter this line into your terminal to install the project's Python dependencies:
`pip3 install -r requirements.txt`

### Set up a .env file
This project has environment variables which are stored in a `.env` file. To create this file, create a nameless file with the `.env` extension in the `/pithiaesc` folder inside of the project's root folder, then, enter in the variable names and their values - listed below are the variable names and short descriptions on setting up them up:
- `SECRET_KEY` - Django uses a `SECRET_KEY` variable to [generate hashes](https://stackoverflow.com/questions/7382149/whats-the-purpose-of-django-setting-secret-key). A value for this variable can be generated by running `python -c "import secrets; print(secrets.token_urlsafe())"` ([SOURCE](https://humberto.io/blog/tldr-generate-django-secret-key/)) in your terminal (assuming you installed the latest version of Python (which is **Python 3.10.4** at the time of writing) when setting up Django earlier). Set the string printed out from this command as the value for this variable.

- `MONGODB_CONNECTION_STRING` - The url used to connect to the MongoDB database. If you followed the [official Install MongoDB guide](https://www.mongodb.com/docs/guides/server/install/), the value for this variable should be `mongodb://localhost:27017`.
- `DB_NAME` - The name of the MongoDB database where metadata file information is stored. Set this to `pithiaesc`.
- `UTIL_DB_NAME` - The name of the MongoDB database where Django utility-related things are stored (e.g. session data, migrations). Set this to `django`.

The contents of the .env file should look like this (with `<the value of the secret key you generated>` substituted with the actual value of the secret key you generated):
```
SECRET_KEY=<the value of the secret key you generated>
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
DB_NAME=pithiaesc
UTIL_DB_NAME=django
```

### Run the project locally
Now that project's Python dependencies, the MongoDB database and the .env file are set up, you should now be able to run the project locally within your web browser. To do this, if you are not already in the root project folder in your terminal, first, navigate to the root project folder from your terminal (e.g., `cd ~/Documents/Projects/pithia-esc-gui-poc`) and activate the project's virtual environment, then enter in one of the following lines, depending on your operating system, into your terminal:
- **MacOS/Linux**: `python3 manage.py runserver`
- **Windows**: `py manage.py runserver`

[SOURCE](https://docs.djangoproject.com/en/4.0/intro/tutorial01/#the-development-server)

If successful, the project should be running on your localhost server at port 8000, where you can access the home page at this address: [http://localhost:8000](http://localhost:8000). Click the link to try it out!
