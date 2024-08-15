import logging
from multiprocessing import Process, Queue
import os

class Logs:
    def __init__(self, log_file="server.log"):
        self.log_file = log_file

    def configurar_logger(self):
        logging.basicConfig(filename=self.log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger()

    def iniciar_logs(self, log_queue):
        log_process = Process(target=self.log_listener, args=(log_queue,))
        log_process.start()
        return log_process

    def log_listener(self, log_queue):
        self.configurar_logger()
        while True:
            log_message = log_queue.get()
            if log_message is None:
                break  # Señal para terminar el proceso
            log_type = log_message.get('type')
            message = log_message.get('message')
            if log_type == 'ERROR':
                self.logger.error(message)
            else:
                self.logger.info(message)

if __name__ == "__main__":
    log_queue = Queue()
    logger = Logs()
    log_process = logger.iniciar_logs(log_queue)
    print(f"PID del log_process: {log_process.pid}")
    log_process.join()