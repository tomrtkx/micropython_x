import socket

class listener_socket:
    def __init__(self, ip_address: str = "", port_number: int = 80):
        self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sck.bind((ip_address, port_number))
        self.sck.listen()

    def send_response(self, conn, response_data: str = "", allow_origin: str = "*"):
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(response_data)}\r\n"
            f"Access-Control-Allow-Origin: {allow_origin}\r\n"
            "Connection: close\r\n"
            f"\r\n{response_data}"
        )
        conn.sendall(response.encode())
        conn.close()

    def receive(self) -> dict:
        conn, addr = self.sck.accept()
        received = conn.recv(1024).decode()
        params = self.parse_request(received)
        return {
            "connection": conn,
            "client": addr,
            "params": params
        }
    
    def parse_request(self, received: str) -> dict:
        type,_,tmp = received.partition(' ')
        path,_,tmp = tmp.partition('?')
        params,_,tmp = tmp.partition(' ')
        params = params.split('&')
        variables = {}
        for v in params:
            vs = v.split('=')
            variables[vs[0]] = vs[1]
        n1 = tmp.find('Host:')
        n2 = tmp.find('\r\n',n1)
        host = tmp[n1:n2].replace("Host:","").strip()
        return {
            "type": type,
            "path": path,
            "variables": variables,
            "host": host
        }

    def close(self):
        self.sck.close()

    def _example_receive_workflow(self):
        print("Waiting for request...")
        req = self.receive()
        print("Received request")
        # 
        # Do something
        #
        self.send_response(req['connection'], response_data = "TEST_RESPONSE")
        print("Connection closed")
        return req

# -------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    print("listener_scoeket - simple test")
    SCK = listener_socket(port_number = 12345)
    print("Listener waits on port: 12345")
    req = SCK.receive()
    print(f"Received request:\n\n{req}\n\n")
    SCK.send_response(req['connection'], response_data = "TEST_RESPONSE")
    print("Connection closed")
    SCK.close()
    print("Socket closed")