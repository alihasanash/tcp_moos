import socket
import json
import pymoos

class TCPJsonToMOOS:
    def __init__(self, tcp_port=5001, moos_host="localhost", moos_port=9000):
        self.tcp_port = tcp_port
        self.comms = pymoos.comms()
        self.comms.set_on_connect_callback(lambda: True)
        self.comms.run(moos_host, moos_port, "TCPJsonToMOOS")

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind(("", self.tcp_port))
            server.listen()
            print(f"Listening on TCP port {self.tcp_port}")

            while True:
                conn, _ = server.accept()
                with conn, conn.makefile('r') as client_file:
                    for line in client_file:
                        try:
                            json_data = json.loads(line.strip())
                            sent = False
                            for k in ("NAV_INFO", "MAP_INFO", "WAYPT_NAV", "WAYPT_NEXT", "AREA_NAV"):
                                if k in json_data:
                                    if k == "WAYPT_NAV" or k == "WAYPT_NEXT" or k == "AREA_NAV":
                                        self.comms.notify(k, json_data[k])
                                    else:
                                        self.comms.notify(k, json.dumps(json_data[k]))
                                    sent = True
                            print("DATA SENT!")
                            if not sent:
                                print("No NAV_INFO, MAP_INFO, WAYPT_NAV, OR AREA_NAV found in JSON")
                        except json.JSONDecodeError:
                            print("Invalid JSON received")

if __name__ == "__main__":
    TCPJsonToMOOS().start()
