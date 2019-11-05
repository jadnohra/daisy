import json
import socket
import threading
import queue
import time

def send_object(socket, object):
    return _send_payload(socket, _object_to_payload(object))
    
def send_object_to_addr(ip_port, object):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
    sock.connect((ip_port[0], int(ip_port[1])))
    send_object(sock, object)
    sock.close()

def receive_objects(socket_conn, msg_extractor):
    payload_part = socket_conn.recv(1024)
    msgs = msg_extractor.process_payload(payload_part)
    objects = [_string_to_object(x) for x in msgs]
    return objects

def receive_objects_from_addr(ip_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
    sock.bind((ip_port[0], int(ip_port[1])))
    sock.listen(1)
    conn, addr = sock.accept()
    extractor = MessageExtractor()
    objects = []
    while len(objects) == 0 or extractor.is_partial():
        objects.extend(receive_objects(conn, extractor))
    conn.close()
    return objects


class Sender:
    def __init__(self, server_ip_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        self.sock.connect((server_ip_port[0], int(server_ip_port[1])))
        
    def send(self, object):
        send_object(self.sock, object)

class Receiver:
    class _DaemonThread(threading.Thread):
        def __init__(self, ip_port, queue):
            super(Receiver._DaemonThread, self).__init__()
            self._ip_port = ip_port
            self._queue = queue
            self._stop_signalled = False
            
        def run(self):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
            sock.bind((self._ip_port[0], int(self._ip_port[1])))
            sock.listen(1)
            conn, addr = sock.accept()
            conn.setblocking(0)
            extractor = MessageExtractor()
            while self._stop_signalled == False:
                try:
                    object_batch = receive_objects(conn, extractor)
                    if len(object_batch):
                        self._queue.put(object_batch)
                except BlockingIOError:
                    time.sleep(0)
            conn.close()

    def __init__(self, ip_port):
        self._queue = queue.Queue()
        self._thread = self._DaemonThread(ip_port, self._queue)
        self._thread.start()
        
    def stop(self):
        self._thread._stop_signalled = True
        
    def receive_objects(self):
        objects = []
        approx_count = self._queue.qsize()
        for i in range(approx_count):
            try:
                objects.extend(self._queue.get_nowait())
            except queue.Empty:
                break
        return objects


def _object_to_payload(object):
    return _string_to_payload(json.dumps(object))

def _string_to_payload(msg):
    return f"[{len(msg)}]{msg}".encode('utf-8')

def _string_to_object(msg):
    return json.loads(msg)

def _send_payload(socket, payload):
    socket.sendall(payload)

class MessageExtractor:
    def __init__(self):
        self._pp_enc = bytes()
        self._pp_dec = ''
        self._next_msg_size = None
        self._next_msg = None
        
    def _store_payload(self, pp_enc):
        self._pp_enc = self._pp_enc + pp_enc
        try:
            pp_dec = self._pp_enc.decode('utf-8')
            self._pp_enc = bytes()
            self._pp_dec = self._pp_dec + pp_dec
        except UnicodeDecodeError:
            for i in range(len(self._pp_enc), 0, -1):
                try:
                    pp_dec = pp_enc[:i].decode('utf-8')
                    self._pp_dec = self._pp_dec + pp_dec
                    self._pp_enc = self._pp_enc[i:]
                    return
                except UnicodeDecodeError:
                    continue
    
    def _parse_header(self, text):
        number_start_i = -1
        number_end_i = -1
        for i in range(len(text)):
            if i == 0:
                if text[i] != '[':
                    raise Exception('')
            else:
                number_start_i = 1
                if text[i] == ']':
                    number_end_i = i-1
                    break
                else:
                    if text[i].isdigit() == False:
                        raise Exception('')
        if number_start_i == -1 or number_end_i == -1:
            return text, None
        else:
            return text[number_end_i+2:], int(text[number_start_i:number_end_i+1])
    
    def _parse_msg(self, text, msg_size):
        if len(text) >= msg_size:
            return text[msg_size:], text[:msg_size]
        else:
            return text, None
        
    def _ensure_next_msg_size(self):
        if self._next_msg_size is not None:
            return True
        pp_dec_left, msg_size = self._parse_header(self._pp_dec)
        if msg_size is not None:
            self._next_msg_size = msg_size
            self._pp_dec = pp_dec_left
            return True
        return False
        
    def _ensure_next_msg(self):
        if self._next_msg is not None:
            return True
        if self._next_msg_size is None:
            raise Exception('')
        pp_dec_left, msg = self._parse_msg(self._pp_dec, self._next_msg_size)
        if msg is not None:
            self._next_msg = msg
            self._pp_dec = pp_dec_left
            return True
        return False
        
    def _get_next_msg(self):
        ret = self._next_msg
        self._next_msg = None
        self._next_msg_size = None
        return ret

    def is_empty(self):
        return len(self._pp_enc) + len(self._pp_dec) == 0

    def is_partial(self):
        return not self.is_empty()
            
    def process_payload(self, partial_payload):
        if partial_payload is None:
            return []
        self._store_payload(partial_payload)
        msgs = []
        while True:
            if self._ensure_next_msg_size() == False:
                break
            if self._ensure_next_msg() == False:
                break
            msgs.append(self._get_next_msg())
        return msgs

def _test_extractor():
    test_string = '''Sîne klâwen durh die wolken sint geslagen,
    er stîget ûf mit grôzer kraft,
    ich sih in grâwen tägelîch als er wil tagen,
    den tac, der im geselleschaft
    erwenden wil, dem werden man,
    den ich mit sorgen în verliez.
    ich bringe in hinnen, ob ich kan.
    sîn vil manegiu tugent michz leisten hiez.'''
    
    test_strings = [test_string[:40], test_string[5:12], test_string[50:72]]
                        
    byte_stream = bytes()
    for test_str in test_strings:
        byte_stream = byte_stream + _string_to_payload(test_str)
        
    extr = MessageExtractor()
    chunk_size = 3
    processed_bytes = 0
    while processed_bytes < len(byte_stream):
        next_chunk_size = min(len(byte_stream)-processed_bytes, chunk_size)
        msgs = extr.process_payload(byte_stream[processed_bytes:processed_bytes+next_chunk_size])
        processed_bytes = processed_bytes + next_chunk_size
        for msg in msgs:
            print('msg', msg)
    print(extr.is_empty())

def _test_sending():
    try:
        ip_port = ('localhost', 4996)

        object = {'hello':1, 'net':'msg'}
        send_object_to_addr(ip_port, object)
    except ConnectionRefusedError:
        pass

    try:
        ip_port = ('localhost', 4997)

        time.sleep(1)
        sender = Sender(ip_port)
        for i in range(10):
            time.sleep(1)
            sender.send(f"hello_{i}")
    except ConnectionRefusedError:
        pass
        
def _test_receiving():
    ip_port = ('localhost', 4996)

    objects = receive_objects_from_addr(ip_port)
    for obj in objects:
        print(obj)

    ip_port = ('localhost', 4997)

    receiver = Receiver(ip_port)
    while True:
        time.sleep(0.5)
        objects = receiver.receive_objects()
        for obj in objects:
            print(obj)
