import socket
import os

#创建套接字
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#address and port
server_socket.bind(('127.0.0.1', 49152))
#listen and one in line
server_socket.listen(1)
print('Server is ready to receive')

#接受请求
while True:
    client_socket, client_addr = server_socket.accept()
    print(f'Connetion is from {client_addr}')

    #wait for the data from client
    while True:
        request = client_socket.recv(1024)#max bytes 1024
        if not request:
            break

        text = request.decode('utf-8')
        print('Message received: ', text)

        #解析请求
        request_lines = text.split('\n')
        if len(request_lines) > 0 and 'GET' in request_lines[0]:
            path = request_lines[0].split(' ')[1]
            if path == '/':
                path = '/index.html'
            #路径转换
            file_path = '.' + path

            if os.path.isfile(file_path):
                if file_path.endswith('.html'):
                    content_type = 'text/html'
                elif file_path.endswith('.jpeg'):
                    content_type = 'image/jpeg'
                else:
                    response = ("HTTP/1.1 404 Not Found\r\n"
                                "Content-Type: text/html\r\n"
                                "Content-Length: 13\r\n\r\n404 Not Found")
                    client_socket.sendall(response.encode())
                    continue

                with open(file_path, 'rb') as f1:
                    content = f1.read()

                #创建HTTP响应信息
                response = (f"HTTP/1.1 200 OK\r\n"
                            f"Content-Type: {content_type}\r\n"
                            f"Content-Length: {len(content)}\r\n\r\n")
                client_socket.sendall(response.encode() + content)

            else: #404
                response = ("HTTP/1.1 404 Not Found\r\n"
                            "Content-Type: text/html\r\n"
                            "Content-Length: 13\r\n\r\n404 Not Found")
                client_socket.sendall(response.encode())

    client_socket.close()




