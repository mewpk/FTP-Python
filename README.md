# Simple FTP Client

This script provides a straightforward command-line interface for interacting with FTP servers. It supports basic FTP operations such as connecting to a server, logging in, navigating directories, and transferring files.

## Features

- **Connect to an FTP Server**: Specify a host and port to establish a connection.
- **User Authentication**: Login with a username and password, with support for anonymous logins.
- **File Operations**: List directory contents, upload, download, delete, and rename files.
- **Directory Navigation**: Change and view the current directory.
- **Transfer Mode Selection**: Switch between ASCII and Binary transfer modes.
- **Session Termination**: Quit the application and close the server connection gracefully.

## Usage

1. **Running the Script**:
   - Launch the script in a terminal or command-line interface.

2. **Connecting to an FTP Server**:
   - Use `open <hostname> [port]` to connect. The default port 21 is used if none is specified.

3. **Logging In**:
   - You'll be prompted for a username and password upon connection. Alternatively, use `login <username> <password>`.

4. **Managing Files and Directories**:
   - `ls` to list files in the current directory.
   - `cd <directory>` to change the current directory.
   - `get <filename>` to download a file.
   - `put <filename>` to upload a file to the server.

5. **Additional Commands**:
   - `pwd` displays the current directory on the FTP server.
   - `ascii` or `binary` to set the file transfer mode.
   - `delete <filename>` and `rename <oldname> <newname>` for file management.

6. **Quitting the Program**:
   - Use `quit` or `bye` to end the session and close the application.

## Requirements

- Python 3.x
- Access to a command-line interface or terminal

## Note

This FTP client is designed for basic use and educational purposes. Ensure you have permission to access and interact with the target FTP server. This script may not handle all potential errors or use cases.

