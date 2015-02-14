#!/usr/bin/python



import multiprocessing
import socket

def handle(connection, address):
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("process-%r" % (address,))
    try:
        logger.debug("Connected %r at %r", connection, address)
        while True:
            data = connection.recv(1024)
            if data == "":
                logger.debug("Socket closed remotely")
                break
            logger.debug("Received data %r", data)
	    
	    request = Request(data)
	    if request.isValid():
	    	connection.sendall(request.response());
		logger.debug("Response Sent") 
	    else:
		logger.debug("Received invalid Request")
		raise TypeError("Invalid Request") 
    except:
        logger.exception("Problem handling request")
    finally:
        logger.debug("Closing socket")
        connection.close()

class Request(object):
    INVALID = "INVALID"
    def __init__(self, data):
	self.method = self.INVALID
	self.data = data
    
    def response(self):
	if not self.isValid():
		raise TypeError("Request is Invalid, no response available")
	return "irrelevant"

    def isValid(self): 
	return self.method != self.INVALID
	
class Server(object):
    def __init__(self, hostname, port):
        import logging
        self.logger = logging.getLogger("server")
        self.hostname = hostname
        self.port = port

    def start(self):
        self.logger.debug("listening")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)

        while True:
            conn, address = self.socket.accept()
            self.logger.debug("Got connection")
            process = multiprocessing.Process(target=handle, args=(conn, address))
            process.daemon = True
            process.start()
            self.logger.debug("Started process %r", process)


    def stop(self):
	self.socket.close()

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    server = Server("127.0.0.1", 1344)
    try:
        logging.info("Listening")
        server.start()
    except:
        logging.exception("Unexpected exception")
    finally:
        logging.info("Shutting down")
	server.stop()
        for process in multiprocessing.active_children():
            logging.info("Shutting down process %r", process)
            process.terminate()
            process.join()
    logging.info("All done")
