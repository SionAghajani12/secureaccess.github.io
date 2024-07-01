import ssl
import socket

def check_lucky_thirteen(host, port):
    try:
        context = ssl.create_default_context()
        connection = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=host)
        connection.connect((host, port))
        
        # Attempt a connection to see if it throws a VulnerabilityError
        connection.recv(1024)
        
        print(f"The server {host}:{port} is vulnerable to Lucky Thirteen.")
    
    except ssl.SSLError as e:
        if "VulnerabilityError" in str(e):
            print(f"The server {host}:{port} is not vulnerable to Lucky Thirteen.")
        else:
            print(f"An SSL error occurred: {e}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
def main():
    host = input("Enter the hostname or IP address of the server: ")
    port = int(input("Enter the port number of the server: "))
    check_lucky_thirteen(host, port)

if __name__ == "__main__":
    main()
