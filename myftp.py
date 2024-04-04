import socket
import os

class FTPClient:
    def __init__(self):
        self.control_socket = None
        self.data_socket = None
        self.data_listener = None  # Listener socket for PORT mode
        self.is_connected = False
        self.host = None
        self.port = None

    def connect(self, host, port=21):
        try:
            self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.control_socket.connect((host, port))
            self.host = host
            self.port = port
            self.is_connected = True
            response = self._read_response()
            print(response , end="")
            self._prompt_for_login()
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    def _prompt_for_login(self):
        response = self.send_command("OPTS UTF8 ON")
        print(response , end="")
        username = input(f"User ({self.host}:(none)): ").strip()
        if username:
            response = self.send_command(f"USER {username}")
            print(response , end="")
            password = input("Password: ").strip()
            response = self.send_command(f"PASS {password}")
            print(response , end="")

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
            print("Not connected to any server. Use 'open <hostname> [port]' to connect.")
            return None
        self.control_socket.sendall(f"{command}\r\n".encode('utf-8'))
        return self._read_response()

    def login(self):
        if not self.is_connected:
            print("You are not connected to any server.")
            return
        username = input(f"Username ").strip()
        if username:
            response = self.send_command(f"USER {username}")
            print(response , end="")
            if "503" in response:
                print("Login failed.")
                return
            password = input("Password: ").strip()
            response = self.send_command(f"PASS {password}")
            print(response , end="")

    def port_mode(self):
        if self.data_socket:
            self.data_socket.close()
            self.data_socket = None
        if self.data_listener:
            self.data_listener.close()
            self.data_listener = None

      
        self.data_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip, port = "127.0.0.1" , 3434
        self.data_listener.bind((ip , port))  # Bind to an available port
        self.data_listener.listen(8)  # Listen for a connection

        p1, p2 = port // 256, port % 256
        port_command = f"PORT {ip.replace('.' , ',')},{p1},{p2}"

        response = self.send_command(port_command)
        print(response , end="")

        return response

    def list_files(self , directory = "" , filename = "" ):
        if not self.is_connected:
            print("You are not connected to any server.")
            return
        
        if not self.port_mode():
            print("Failed to enter port mode.")
            return
        
        command_message = "NLST"
        if directory:
            command_message += f" {directory}"
        response = self.send_command(command_message)

        print(response , end="")
        

        try:
            self.data_socket, _ = self.data_listener.accept()
            return True
        except Exception as e:
            print(f"Failed to establish data connection in PORT mode: {e}")
            return False
        finally:
            file_list = self._read_data()
            if (filename):
                with open(filename, 'w') as file:
                    file.write(file_list)
            else :
                print(file_list, end="")
                
            if self.data_listener:
                self.data_listener.close()
                self.data_listener = None
            response = self._read_response()
            print(response, end="")
           

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
        self.data_socket = None

        return data

    def get_file(self, remote_target="" , local_target=""):
        if not self.port_mode():
            print("Could not enter port mode.")
            return
        if not remote_target:
            remote_target = input("Remote file ")
            local_target = input("Local file ")

        print(self.send_command(f"RETR {remote_target}"),end="")
        try:
            self.data_socket, _ = self.data_listener.accept()
            return True
        except Exception as e:
            print(f"Failed to establish data connection in PORT mode: {e}")
            return False
        finally:
            if local_target:
                local_target = os.getcwd()+"\\"+local_target
            with open(local_target, 'wb') as f:
                while True:
                    data = self.data_socket.recv(4096)
                    if not data:
                        break
                    f.write(data)
            if self.data_listener:
                self.data_listener.close()
                self.data_listener = None
            file_list = self._read_response()
            print(file_list, end="")


    def put_file(self, remote_target="", local_target=""):
        if not self.port_mode():
            print("Could not enter port mode.")
            return
        if not local_target:  # If no local file is specified, ask the user for it.
            local_target = input("Local file: ")
            remote_target = input("Remote file (leave blank to use the local file name): ") or os.path.basename(local_target)
        # Check if the local file exists before attempting to upload.
        if not os.path.isfile(local_target):
            print(f"Local file does not exist: {local_target}")
            return

        response = self.send_command(f"STOR {remote_target}")
        print(response, end="")

        try:
            self.data_socket, _ = self.data_listener.accept()
            with open(local_target, 'rb') as f:
                while True:
                    data = f.read(4096)
                    if not data:
                        break
                    self.data_socket.send(data)
        except Exception as e:
            print(f"Failed to upload {remote_target}: {e}")
        finally:
            if self.data_socket:
                self.data_socket.close()
                self.data_socket = None
            if self.data_listener:
                self.data_listener.close()
                self.data_listener = None
            response = self._read_response()
            print(response, end="")

    def change_directory(self, directory):
        if not self.is_connected:
            print("You are not connected to any server.")
            return

        print(self.send_command(f"CWD {directory}"),end="")


    def print_working_directory(self):
        print(self.send_command("PWD"),end="")

    def quit(self):
        print(self.send_command("QUIT"),end="")
        self.control_socket.close()
        self.is_connected = False


    def set_transfer_mode(self, mode):
        """Set the file transfer mode to ASCII or Binary."""
        if mode.lower() == 'ascii':
            print(self.send_command("TYPE A"),end="")
        elif mode.lower() == 'binary':
            print(self.send_command("TYPE I"),end="")
        else:
            print("Unknown mode. Use 'ascii' or 'binary'.",end="")

    def delete_file(self, filename=""):
        """Delete a file on the server."""
        if not filename:
            filename = input("Remote file :")

        print(self.send_command(f"DELE {filename}"),end="")

    def rename_file(self, old_name, new_name):
        response = self.send_command(f"RNFR {old_name}")
        print(response, end="")
        if "350" in response:  # Server is ready for the new file name
            response = self.send_command(f"RNTO {new_name}")
            print(response, end="")
    def rename_filev2(self):
        old_name = input("From name ")
        new_name = input("To name ")
        response = self.send_command(f"RNFR {old_name}")
        print(response, end="")
        if "350" in response:  # Server is ready for the new file name
            response = self.send_command(f"RNTO {new_name}")
            print(response, end="")



def main():
    ftp = FTPClient()
    print("Simple FTP client\nType 'help' for a list of commands.")

    while True:
        cmd = input("ftp> ").strip().split()
        action = cmd[0].lower() if cmd else 'help'

        if action == 'quit' or action == 'bye':
            if ftp.is_connected:
                ftp.quit()
            else:
                print("Bye!")
            break
        elif action == 'open':
            if ftp.is_connected :
                print(f"Already connected to {ftp.host}. Use disconnect first.")
                continue
            if len(cmd) < 2:
                host = input("to ").strip()
                port = 21
            else :
                host = cmd[1]
                port = int(cmd[2]) if len(cmd) == 3 else 21
            if ftp.connect(host, port):
                continue
        elif action == 'user':
            ftp.login()
        elif action == 'ls':
            if len(cmd) == 3:
                ftp.list_files(cmd[1], cmd[2])
            elif len(cmd) == 2:
                ftp.list_files(cmd[1])
            else:
                ftp.list_files()
        elif action == 'get' :
            if len(cmd) == 3 :
                ftp.get_file(cmd[1], cmd[2])
            elif len(cmd) == 2:
                ftp.get_file(cmd[1])
            else :
                ftp.get_file()
        elif action == 'put' :
            if len(cmd) == 3 :
                ftp.put_file(cmd[1],cmd[2])
            elif len(cmd) == 2:
                ftp.put_file(cmd[1])
            else :
                ftp.put_file()
            
        elif action == 'cd' and len(cmd) == 2:
            ftp.change_directory(cmd[1])
        elif action == 'pwd':
            ftp.print_working_directory()
        elif action == 'ascii' or action == 'binary':
            ftp.set_transfer_mode(action)
        elif action == 'delete' :
            if len(cmd) == 2:
                ftp.delete_file(cmd[1])
            else :
                ftp.delete_file()
        elif action == 'rename' and len(cmd) == 3:
            ftp.rename_file(cmd[1], cmd[2])
        elif action == "rename" :
            ftp.rename_filev2()
        elif action == "close" or action == "disconnect":
            if ftp.is_connected:
                ftp.quit()
            else:
                print("Bye!")
        elif action == 'help':
            print(
                "Commands: open, login, ls, get, put, cd, pwd, ascii, binary, delete, rename, quit ,disconnect ,close ")
        else:
            print("Unknown command. Type 'help' for a list of commands.")


if __name__ == "__main__":
    main()
