import socket

# get local ip and hostname
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)


SEVER_HOST = local_ip

SEVER_PORT = 80

# get IP address
print ("Local IP "+local_ip)

# Create socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((SEVER_HOST, SEVER_PORT))

# start to run the server
serverSocket.listen(5)
print ("Listening to socket "+ str(SEVER_HOST))
print ("Listening on Port " + str(SEVER_PORT))

while True:
    # wait for client connections
    clientConnection, clientAddress = serverSocket.accept()
    # get the client request
    request = clientConnection.recv(1024).decode()
    print (request)
    print ("Connection from" + str(clientAddress))
    # get HTML file content
    # Parse HTTP headers
    headers = request.split('\n')
    filename = headers[0].split()[1]

    print ("Request: ", filename)
    # get the content of the file
    if filename == '/':
        filename = '/webpagesample.html'
    link = 'webpages'+filename

    # try to open and read webpage as a file
    try:
        webPage = open(link,'rb')
        content = webPage.read()
        webPage.close()
        # add HTTP header if file successfully opened
        header = 'HTTP/1.1 200 OK\n'
        header += 'Content-type: text/html\n\n'
    except  FileNotFoundError:
        # if no such file
        # send 404 NOT FOUND error
        print ("404 File not found")
        header = 'HTTP/1.1 404 NOT FOUND\n\n'
        content = '404 NOT FOUND\n'.encode('utf-8')

    # send HTTP response
    response = header.encode('utf-8')
    response+= content
    clientConnection.send(response)
    # close client connection
    clientConnection.close()

# close server connection
serverSocket.close()


