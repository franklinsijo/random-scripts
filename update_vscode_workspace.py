#!/usr/bin/env python3

import os
import json

# Path relative to the HOME directory or the absolute path of the directory containing folders 
# that are to be added to the VSCode Workspace
WORKSPACE_DIRECTORY='Workspace/Github'
# Path relative to the HOME directory or the absolute path of the Workspace configuration file
VSCODE_SETTINGS_FILE='Workspace/franklinsijo.code-workspace'

ABSOLUTE_WORKSPACE_DIRECTORY=os.path.abspath(os.path.join(os.environ['HOME'], WORKSPACE_DIRECTORY))
ABSOLUTE_SETTINGS_FILE=os.path.abspath(os.path.join(os.environ['HOME'], VSCODE_SETTINGS_FILE))

CURRENT_DIRECTORIES=[]
for d in os.listdir(ABSOLUTE_WORKSPACE_DIRECTORY):
    if os.path.isdir(os.path.join(ABSOLUTE_WORKSPACE_DIRECTORY, d)):        
        CURRENT_DIRECTORIES.append({'name': d, 'path': os.path.join(ABSOLUTE_WORKSPACE_DIRECTORY, d)})
SORTED_DIRECTORIES=sorted(CURRENT_DIRECTORIES, key=lambda k:k['name'])
with open(ABSOLUTE_SETTINGS_FILE, 'w') as v:
    v.write(json.dumps({'folders': SORTED_DIRECTORIES}, indent=4))
v.close()

## Auto update whenever the folder changes ##
# nohup fswatch -od -l 60 /Users/frankojis/Workspace/Github/ | xargs -n1 /Users/frankojis/Workspace/Github/random-scripts/update_vscode_workspace.py &
