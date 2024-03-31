Simple FTP Client

This enhanced script provides a user-friendly command-line interface for connecting to and interacting with FTP servers. It includes functionalities for basic file and directory operations on an FTP server, including file transfers, directory navigation, and more sophisticated commands like file renaming and server disconnection.

Features

- Server Connection: Connect to an FTP server with a specified host and port.
- Login and Authentication: Support for logging in with username and password. Enhanced to handle UTF-8 encoding options.
- Directory Navigation: List files, change directories, and print the current directory on the server.
- File Management: Upload (PUT) and download (GET) files, delete files, and rename files directly from the command line.
- Transfer Mode: Select between ASCII and Binary modes for file transfer.
- Session Management: Includes options to quit the application, disconnect, and close the session gracefully.

Usage

1. Starting the Script:
   - Execute the script in a terminal or command-line interface to begin.
   - python myftp.py

2. Connecting to an FTP Server:
   - Use open <hostname> [port] command. If no port is specified, 21 is used by default.

3. Logging In:
   - You'll be automatically prompted for login credentials after a successful connection. Alternatively, use the user command for login prompts.

4. Navigating and Managing Files:
   - Use ls to list files, cd <directory> to change the directory, get <filename> to download files, and put <filename> to upload files.

5. Additional Features:
   - The pwd command shows the current directory.
   - Transfer modes can be switched using ascii or binary. 
   - Files can be deleted with delete <filename> and renamed with rename <oldname> <newname>.

6. Renaming Files:
   - Use rename followed by the old and new filenames to rename a file on the server.

7. Disconnecting:
   - Use quit, bye, disconnect, or close to end the session and disconnect from the server.

Requirements

- Python 3.x
- A terminal or command-line interface

Additional Information

This FTP client script is intended for educational and straightforward operational purposes. It may not cover all error scenarios or be suitable for every FTP server. Always ensure you have the proper permissions to access and interact with an FTP server before use.
