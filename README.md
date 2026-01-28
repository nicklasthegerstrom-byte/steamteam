# Steamteam
Match with other users based on gaming interests.

## About
This project allows users to import their Steam game data and discover other users with similar gaming interests.
By analyzing played games, genres, and game IDs, the application matches users based on shared preferences.
The goal is to help players find like-minded gamers and potential gaming partners through data-driven matching.

## Features
-  User accounts creation system  
-  Game related data via Steam API support  
-  Graphical user interface  
-  User matching algoritm  with data vector technology  
-  SQLite3 for database management  

## Requirements
-  Internet connection
-  Steam account  
-  Steam Web API-key
-  Python3

## Installation
Open a terminal / command prompt and run the following commands.  
During installation replace `python` with `python3` or `py` depending on your system.  
#### 1. Clone the repository and navigate to project folder  
   ```
   git clone https://github.com/nicklasthegerstrom-byte/steamteam.git
   ```
   ```
   cd steamteam
   ```

#### 2. Create and activate a virtual environment  

   - Windows:   
   ```
   python -m venv venv
   ```
   ```  
   venv\Scripts\activate  
   ```
   - MacOS / Linux:  
   ```
   python -m venv venv  
   ```
   ```
   source venv/bin/activate  
   ```

#### 3. Install dependencies  
   ```
   pip install -r requirements.txt
   ```

## Running
Run `app.pyw` from the project root folder:    
```
python app.pyw
```

## Usage  
-  
-  
-  

## Contributors  
   Constantine - [Aeolian0pus](https://github.com/AeolianOpus)  

   Even - [evenhadeghe](https://github.com/evenhadeghe)  

   Nicklas - [nicklasthegerstrom-byte](https://github.com/nicklasthegerstrom-byte)  

   Erik - [ErikCoderMan](https://github.com/ErikCoderMan)  

   Adam - (profile missing)

## Development Workflow

The project structure is set up in the dev branch.
All development work should follow the workflow below.

#### 1. Setup and Branching  
Open your CLI and navigate to the project directory:  
```
   cd "path/to/your/project-folder"
   cd steamteam
   git checkout dev  
   git pull
```
Create a new branch to work in:
```
   git checkout -b feat/matching
```
Branch naming is important.
This is only an example. Use clear and descriptive names such as:
`feat/matching`, `docs/readme`, `db/database`, `test/tests`

The goal is that everyone (and the tech lead) can easily understand what you are working on.  
Pull requests with unclear or misleading branch names may be rejected.  

#### 2. First Push (Important)

The first time you push a new branch, you must run:
```
   git push -u origin <branch-name>
```
This is required unless you have configured a global push.autoSetupRemote.

#### 3. Creating Files Correctly

When creating new files, make sure they are placed in the correct directory from the start.  
Example if settings.py should be located in the data folder:

PowerShell:  
```
   New-Item .\data\settings.py -Force
```
Bash / other shells:  
```
   touch data/settings.py
```

Always verify that files are created in the correct location before starting work.

#### 4. Development and Commits

- Work only inside your own branch.
- Commit your changes properly
- Remember to:
  - Save your files (CTRL + S in VS Code)  
  - Commit your changes properly  

Example:
```  
   git add .
   git commit -m "Clear and descriptive commit message"
   git push
```

#### 5. Pull Request to dev

When your work is complete and ready to be merged:  
- Go to the steamteam repository on GitHub  
- Open the Pull Requests tab  
- Click Create Pull Request  
- Set:
  - Base branch (left): dev
  - Compare branch (right): your feature branch  

Submit the pull request.

#### 6. Review  
The tech lead will review the pull request on GitHub and approve or request changes before merging into dev.
