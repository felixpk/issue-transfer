# GitLab to Github Issue Transfer
Simple script to copy issues from GitLab to Github

## Setup settings.ini

Make a copy of the example settings file `cp settings-example.ini settings.ini`. 

1. Generate GitLab PAT (Profile -> Access Tokens)  
   Paste token to `GITLAB -> token`
2. Generate Github PAT (Settings -> Developer Settings -> Personal Access tokens)  
   Paste token to `GITHUB -> token`
3. Set source project ID `GITLAB -> project-id` (shown in repo home)
4. Define which label(s) an issue must have in order to be tranfered under `GITLAB -> labels`


## Run the script
`python main.py [-d, --dry-run]`