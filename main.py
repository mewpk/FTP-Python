import socket
import re
import os


class FTPClient:
    def __init__(self):
        self.control_socket = None
        self.data_socket = None
        self.is_connected = False

    def connect(self, host, port=21):
        try:
            self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.control_socket.connect((host, port))
            self.is_connected = True
            response = self._read_response()
            print(response)

            # Prompt for username and password right after connection.
            self._prompt_for_login()

            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    def _prompt_for_login(self):
        username = input("User: ").strip()
        if username:
            response = self.send_command(f"USER {username}")
            print(response)
            password = input("Password: ").strip()
            response = self.send_command(f"PASS {password}")
            print(response)


    def _read_response(self):
        response = ''
        while True:
            chunk = self.control_socket.recv(4096).decode('utf-8')
            if not chunk:
                break
            response += chunk
            if chunk.endswith('\r\n'):
                break
        return response

    def send_command(self, command):
        if not self.is_connected:
            print(
                "Not connected to any server. Use 'open <hostname> [port]' to connect.")
            return None  # Ensure a None response is intentionally returned.
        self.control_socket.sendall(f"{command}\r\n".encode('utf-8'))
        return self._read_response()

    def login(self, username='anonymous', password=''):
        print(self.send_command(f"USER {username}"))
        print(self.send_command(f"PASS {password}"))


    def pasv_mode(self):
        response = self.send_command("PASV")
        if response is None:  # Check if response is None before proceeding.
            return False  # Indicate failure to enter PASV mode.
        print(response)
        # Extract the IP address and port from the response.
        pattern = re.compile(r'(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)')
        match = pattern.search(response)
        if not match:
            print("Failed to enter passive mode.")
            return False
        parts = match.groups()
        data_ip = '.'.join(parts[:4])
        data_port = (int(parts[4]) << 8) + int(parts[5])
        self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_socket.connect((data_ip, data_port))
        return True  # Successfully entered PASV mode.


    def list_files(self):
        if not self.pasv_mode():
            print("Could not enter passive mode. Make sure you're connected to a server.")
            return  # Exit the method if unable to enter PASV mode.
        print(self.send_command("LIST"))
        print(self._read_data())


    def _read_data(self):
        data = ''
        if self.data_socket is None:
            print("Data socket is not available.")
            return data
        while True:
            chunk = self.data_socket.recv(4096).decode('utf-8')
            if not chunk:
                break
            data += chunk
        self.data_socket.close()
        self.data_socket = None  # Reset the data socket to None after closing.
        return data


    def get_file(self, filename):
        if not self.pasv_mode():
            print("Could not enter passive mode. Make sure you're connected to a server.")
            return  # Exit the method if unable to enter PASV mode.
        print(self.send_command(f"RETR {filename}"))
        with open(filename, 'wb') as f:
            while True:
                data = self.data_socket.recv(4096)
                if not data:
                    break
                f.write(data)
        print(f"{filename} has been downloaded.")
        self.data_socket.close()

    def put_file(self, filename):
        if not self.pasv_mode():
            print("Could not enter passive mode. Make sure you're connected to a server.")
            return  # Exit the method if unable to enter PASV mode.
        print(self.send_command(f"STOR {filename}"))
        with open(filename, 'rb') as f:
            while True:
                data = f.read(4096)
                if not data:
                    break
                self.data_socket.send(data)
        print(f"{filename} has been uploaded.")
        self.data_socket.close()

    def change_directory(self, directory):
        print(self.send_command(f"CWD {directory}"))

    def print_working_directory(self):
        print(self.send_command("PWD"))

    def quit(self):
        print(self.send_command("QUIT"))
        self.control_socket.close()
        self.is_connected = False

    def set_transfer_mode(self, mode):
        """Set the file transfer mode to ASCII or Binary."""
        if mode.lower() == 'ascii':
            print(self.send_command("TYPE A"))
        elif mode.lower() == 'binary':
            print(self.send_command("TYPE I"))
        else:
            print("Unknown mode. Use 'ascii' or 'binary'.")

    def delete_file(self, filename):
        """Delete a file on the server."""
        print(self.send_command(f"DELE {filename}"))

    def rename_file(self, old_name, new_name):
        """Rename a file on the server."""
        print(self.send_command(f"RNFR {old_name}"))
        print(self.send_command(f"RNTO {new_name}"))


def main():
    ftp = FTPClient()
    print("Simple FTP client\nType 'help' for a list of commands.")

    while True:
        cmd = input("FTP> ").strip().split()
        action = cmd[0].lower() if cmd else 'help'

        if action == 'quit' or action == 'bye':
            ftp.quit()
            print("Goodbye!")
            break
        elif action == 'open' and len(cmd) >= 2:
            host = cmd[1]
            port = int(cmd[2]) if len(cmd) == 3 else 21
            if ftp.connect(host, port):
                # Connection successful, login handled within connect method
                pass
        elif action == 'login' and len(cmd) >= 3:
            ftp.login(cmd[1], cmd[2])
        elif action == 'ls':
            ftp.list_files()
        elif action == 'get' and len(cmd) == 2:
            ftp.get_file(cmd[1])
        elif action == 'put' and len(cmd) == 2:
            ftp.put_file(cmd[1])
        elif action == 'cd' and len(cmd) == 2:
            ftp.change_directory(cmd[1])
        elif action == 'pwd':
            ftp.print_working_directory()
        elif action == 'ascii' or action == 'binary':
            ftp.set_transfer_mode(action)
        elif action == 'delete' and len(cmd) == 2:
            ftp.delete_file(cmd[1])
        elif action == 'rename' and len(cmd) == 3:
            ftp.rename_file(cmd[1], cmd[2])
        elif action == 'help':
            print(
                "Commands: open, login, ls, get, put, cd, pwd, ascii, binary, delete, rename, quit")
        else:
            print("Unknown command. Type 'help' for a list of commands.")


if __name__ == "__main__":
    main()
