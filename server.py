import socket
import sys
import os

PORT_IDX = 1
GET_MSG_IDX = 0
FILE_NAME_IDX = 1
CONNECTION_LINE_IDX = 2
CONNECTION_VALUE_IDX = 1
RECV_TIMEOUT = 1
BASE_DIR = './files'
CLOSE_CONN = 'close'
ALIVE_CONN = 'keep-alive'
OK = 'HTTP/1.1 200 OK'
NOT_FOUND = 'HTTP/1.1 404 Not Found'
MOVED_PERMANENTLY = 'HTTP/1.1 301 Moved Permanently'
image_extensions = ['jpg', 'ico']


def default(requested_file, connection):
    response = ''
    temp_name = requested_file.split('.')
    extension = temp_name[len(temp_name)-1]

    # check if it's image
    if extension in image_extensions:
        mode = 'rb'
        file_data = []
    else:
        mode = 'r'
        file_data = ""

    # read information and concaticate the message
    try:
        file = open(BASE_DIR + '/' + requested_file, mode)
        response = OK
        file_data = file.read()
        file.close()
        msg = response + '\r\nConnection: ' + connection + \
            '\r\nContent-Length: ' + str(len(file_data)) + '\r\n\r\n'
        if mode == 'rb':
            msg = msg.encode() + file_data
        else:
            msg += file_data
            msg = msg.encode()

    # could not open the file
    except:
        response = NOT_FOUND
        connection = CLOSE_CONN
        msg = response + '\r\nConnection: ' + connection
        msg = msg.encode()
    return msg, connection


def empty(requested_file, connection):
    return default('index.html', connection)


def redirect(requested_file, connection):
    location = '/result.html'
    response = MOVED_PERMANENTLY
    connection = CLOSE_CONN
    msg = response + '\r\nConnection: ' + connection + \
        '\r\nLocation: ' + location + '\r\n'
    msg = msg.encode()
    return msg, connection


def main():
    # listen to anybody
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = int(sys.argv[PORT_IDX])
    server.bind(('0.0.0.0', port))
    server.listen(5)

    while True:
        # accept connection
        client_socket, client_address = server.accept()
        client_socket.settimeout(RECV_TIMEOUT)
        connection = ALIVE_CONN

        # communication with one client
        while connection == ALIVE_CONN:
            try:
                data = client_socket.recv(1024).decode()

                # parse data recieved
                if data != '':
                    print(data)
                    data = data.split('\r\n')
                    requested_file = data[GET_MSG_IDX].split(' ')[
                        FILE_NAME_IDX][1:]
                    connection = data[CONNECTION_LINE_IDX].split(
                        ': ')[CONNECTION_VALUE_IDX]

                    # switch case
                    switcher = {
                        '': empty,
                        'redirect': redirect
                    }
                    msg, connection = switcher.get(
                        requested_file, default)(requested_file, connection)

                    # send message to client
                    client_socket.send(msg)

            # communication terminated after 1 sec of none requests
            except:
                connection = CLOSE_CONN
                client_socket.close()


if __name__ == "__main__":
    main()
