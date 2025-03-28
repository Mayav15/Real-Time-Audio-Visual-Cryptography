import cv2
import pyautogui
import numpy as np

import socket
import pickle
import struct
import threading

import pyaudio
import select

import tkinter as tk
import random
import hashlib
import math
import rsa

class StreamingServer:
    """
    Class for the streaming server.

    Attributes
    ----------

    Private:

        __host : str
            host address of the listening server
        __port : int
            port on which the server is listening
        __slots : int
            amount of maximum avaialable slots (not ready yet)
        __used_slots : int
            amount of used slots (not ready yet)
        __quit_key : chr
            key that has to be pressed to close connection
        __running : bool
            inicates if the server is already running or not
        __block : Lock
            a basic lock used for the synchronization of threads
        __server_socket : socket
            the main server socket


    Methods
    -------

    Private:

        __init_socket : method that binds the server socket to the host and port
        __server_listening: method that listens for new connections
        __client_connection : main method for processing the client streams

    Public:

        start_server : starts the server in a new thread
        stop_server : stops the server and closes all connections
    """

    # TODO: Implement slots functionality
    def __init__(self, host, port, slots=8, quit_key='q'):
        """
        Creates a new instance of StreamingServer

        Parameters
        ----------

        host : str
            host address of the listening server
        port : int
            port on which the server is listening
        slots : int
            amount of avaialable slots (not ready yet) (default = 8)
        quit_key : chr
            key that has to be pressed to close connection (default = 'q')  
        """
        self.__host = host
        self.__port = port
        self.__slots = slots
        self.__used_slots = 0
        self.__running = False
        self.__quit_key = quit_key
        self.__block = threading.Lock()
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__init_socket()
        self.__reverse_mapping = self.key_generation()
        # self.__key_exchange()

    def __init_socket(self):
        """
        Binds the server socket to the given host and port
        """
        self.__server_socket.bind((self.__host, self.__port))
    
    def __key_exchange(self):
        sender_username = 61
        reveiver_username = 59
        P = 33
        G = 8
        b = 2
        B = pow(G, b, P)
        B_str = str(B)
        B_shahash = hashlib.sha256(B_str.encode()).hexdigest()
        sender_publicKey, sender_privateKey = rsa.newkeys(512)
        B_enc = rsa.encrypt(message.encode(),sender_publicKey)
        packet = (B,B_enc,sender_publicKey)

    def key_generation(self):
        np.random.seed(85)
        original_pool = np.arange(0,256)
        mapping = np.copy(original_pool)
        np.random.shuffle(mapping)
        reverse_mapping_key = dict(zip(mapping, original_pool))
        key_list = np.array(list(reverse_mapping_key.keys()))
        value_list = np.array(list(reverse_mapping_key.values()))
        reverse_mapping = np.zeros(key_list.max()+1,dtype=value_list.dtype)
        reverse_mapping[key_list] = value_list
        return reverse_mapping.astype(np.uint8)
    
    def decrypt_image_frame(self,frame):
        frame = self.__reverse_mapping[frame]
        return frame

    def start_server(self):
        """
        Starts the server if it is not running already.
        """
        if self.__running:
            print("Server is already running")
        else:
            self.__running = True
            server_thread = threading.Thread(target=self.__server_listening)
            server_thread.start()

    def __server_listening(self):
        """
        Listens for new connections.
        """
        self.__server_socket.listen()
        while self.__running:
            self.__block.acquire()
            connection, address = self.__server_socket.accept()
            if self.__used_slots >= self.__slots:
                print("Connection refused! No free slots!")
                connection.close()
                self.__block.release()
                continue
            else:
                self.__used_slots += 1
            self.__block.release()
            thread = threading.Thread(target=self.__client_connection, args=(connection, address,))
            thread.start()

    def stop_server(self):
        """
        Stops the server and closes all connections
        """
        if self.__running:
            self.__running = False
            closing_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            closing_connection.connect((self.__host, self.__port))
            closing_connection.close()
            self.__block.acquire()
            self.__server_socket.close()
            self.__block.release()
        else:
            print("Server not running!")

    def __client_connection(self, connection, address):
        """
        Handles the individual client connections and processes their stream data.
        """
        payload_size = struct.calcsize('>L')
        data = b""

        while self.__running:

            break_loop = False

            while len(data) < payload_size:
                received = connection.recv(4096)
                if received == b'':
                    connection.close()
                    self.__used_slots -= 1
                    break_loop = True
                    break
                data += received

            if break_loop:
                break

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]

            msg_size = struct.unpack(">L", packed_msg_size)[0]

            while len(data) < msg_size:
                data += connection.recv(4096)

            frame_data = data[:msg_size]
            data = data[msg_size:]

            frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
            frame = self.decrypt_image_frame(frame)
            cv2.imshow(str(address), frame)
            if cv2.waitKey(1) == ord(self.__quit_key):
                connection.close()
                self.__used_slots -= 1
                break

class StreamingClient:
    """
    Abstract class for the generic streaming client.

    Attributes
    ----------

    Private:

        __host : str
            host address to connect to
        __port : int
            port to connect to
        __running : bool
            inicates if the client is already streaming or not
        __encoding_parameters : list
            a list of encoding parameters for OpenCV
        __client_socket : socket
            the main client socket


    Methods
    -------

    Private:

        __client_streaming : main method for streaming the client data

    Protected:

        _configure : sets basic configurations (overridden by child classes)
        _get_frame : returns the frame to be sent to the server (overridden by child classes)
        _cleanup : cleans up all the resources and closes everything

    Public:

        start_stream : starts the client stream in a new thread
    """

    def __init__(self, host, port):
        """
        Creates a new instance of StreamingClient.

        Parameters
        ----------

        host : str
            host address to connect to
        port : int
            port to connect to
        """
        self.__host = host
        self.__port = port
        self._configure()
        self.__running = False
        self.__client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__mapping = self.key_generation()

    def key_generation(self):
        np.random.seed(85)
        original_pool = np.arange(0,256)
        mapping = np.copy(original_pool)
        np.random.shuffle(mapping)
        return mapping.astype(np.uint8)
    
    def encrypt_image_frame(self,frame):
        frame = self.__mapping[frame]
        return frame

    def _configure(self):
        """
        Basic configuration function.
        """
        self.__encoding_parameters = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

    def _get_frame(self):
        """
        Basic function for getting the next frame.

        Returns
        -------

        frame : the next frame to be processed (default = None)
        """
        return None

    def _cleanup(self):
        """
        Cleans up resources and closes everything.
        """
        cv2.destroyAllWindows()

    def __client_streaming(self):
        """
        Main method for streaming the client data.
        """
        self.__client_socket.connect((self.__host, self.__port))
        while self.__running:
            frame = self._get_frame()
            frame = self.encrypt_image_frame(frame)
            data = pickle.dumps(frame, 0)
            size = len(data)

            try:
                self.__client_socket.sendall(struct.pack('>L', size) + data)
            except ConnectionResetError:
                self.__running = False
            except ConnectionAbortedError:
                self.__running = False
            except BrokenPipeError:
                self.__running = False

        self._cleanup()

    def start_stream(self):
        """
        Starts client stream if it is not already running.
        """

        if self.__running:
            print("Client is already streaming!")
        else:
            self.__running = True
            client_thread = threading.Thread(target=self.__client_streaming)
            client_thread.start()

    def stop_stream(self):
        """
        Stops client stream if running
        """
        if self.__running:
            self.__running = False
        else:
            print("Client not streaming!")

class CameraClient(StreamingClient):
    """
    Class for the camera streaming client.

    Attributes
    ----------

    Private:

        __host : str
            host address to connect to
        __port : int
            port to connect to
        __running : bool
            inicates if the client is already streaming or not
        __encoding_parameters : list
            a list of encoding parameters for OpenCV
        __client_socket : socket
            the main client socket
        __camera : VideoCapture
            the camera object
        __x_res : int
            the x resolution
        __y_res : int
            the y resolution


    Methods
    -------

    Protected:

        _configure : sets basic configurations
        _get_frame : returns the camera frame to be sent to the server
        _cleanup : cleans up all the resources and closes everything

    Public:

        start_stream : starts the camera stream in a new thread
    """

    def __init__(self, host, port, x_res=1024, y_res=576):
        """
        Creates a new instance of CameraClient.

        Parameters
        ----------

        host : str
            host address to connect to
        port : int
            port to connect to
        x_res : int
            the x resolution
        y_res : int
            the y resolution
        """
        self.__x_res = x_res
        self.__y_res = y_res
        self.__camera = cv2.VideoCapture(0)
        super(CameraClient, self).__init__(host, port)

    def _configure(self):
        """
        Sets the camera resultion and the encoding parameters.
        """
        self.__camera.set(3, self.__x_res)
        self.__camera.set(4, self.__y_res)
        super(CameraClient, self)._configure()

    def _get_frame(self):
        """
        Gets the next camera frame.

        Returns
        -------

        frame : the next camera frame to be processed
        """
        ret, frame = self.__camera.read()
        return frame

    def _cleanup(self):
        """
        Cleans up resources and closes everything.
        """
        self.__camera.release()
        cv2.destroyAllWindows()

class VideoClient(StreamingClient):
    """
    Class for the video streaming client.

    Attributes
    ----------

    Private:

        __host : str
            host address to connect to
        __port : int
            port to connect to
        __running : bool
            inicates if the client is already streaming or not
        __encoding_parameters : list
            a list of encoding parameters for OpenCV
        __client_socket : socket
            the main client socket
        __video : VideoCapture
            the video object
        __loop : bool
            boolean that decides whether the video shall loop or not


    Methods
    -------

    Protected:

        _configure : sets basic configurations
        _get_frame : returns the video frame to be sent to the server
        _cleanup : cleans up all the resources and closes everything

    Public:

        start_stream : starts the video stream in a new thread
    """

    def __init__(self, host, port, video, loop=True):
        """
        Creates a new instance of VideoClient.

        Parameters
        ----------

        host : str
            host address to connect to
        port : int
            port to connect to
        video : str
            path to the video
        loop : bool
            indicates whether the video shall loop or not
        """
        self.__video = cv2.VideoCapture(video)
        self.__loop = loop
        super(VideoClient, self).__init__(host, port)

    def _configure(self):
        """
        Set video resolution and encoding parameters.
        """
        self.__video.set(3, 1024)
        self.__video.set(4, 576)
        super(VideoClient, self)._configure()

    def _get_frame(self):
        """
        Gets the next video frame.

        Returns
        -------

        frame : the next video frame to be processed
        """
        ret, frame = self.__video.read()
        return frame

    def _cleanup(self):
        """
        Cleans up resources and closes everything.
        """
        self.__video.release()
        cv2.destroyAllWindows()

class ScreenShareClient(StreamingClient):
    """
    Class for the screen share streaming client.

    Attributes
    ----------

    Private:

        __host : str
            host address to connect to
        __port : int
            port to connect to
        __running : bool
            inicates if the client is already streaming or not
        __encoding_parameters : list
            a list of encoding parameters for OpenCV
        __client_socket : socket
            the main client socket
        __x_res : int
            the x resolution
        __y_res : int
            the y resolution


    Methods
    -------

    Protected:

        _get_frame : returns the screenshot frame to be sent to the server

    Public:

        start_stream : starts the screen sharing stream in a new thread
    """

    def __init__(self, host, port, x_res=1024, y_res=576):
        """
        Creates a new instance of ScreenShareClient.

        Parameters
        ----------

        host : str
            host address to connect to
        port : int
            port to connect to
        x_res : int
            the x resolution
        y_res : int
            the y resolution
        """
        self.__x_res = x_res
        self.__y_res = y_res
        super(ScreenShareClient, self).__init__(host, port)

    def _get_frame(self):
        """
        Gets the next screenshot.

        Returns
        -------

        frame : the next screenshot frame to be processed
        """
        screen = pyautogui.screenshot()
        frame = np.array(screen)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (self.__x_res, self.__y_res), interpolation=cv2.INTER_AREA)
        return frame

class AudioSender:

    def __init__(self, host, port, audio_format=pyaudio.paInt16, channels=1, rate=44100, frame_chunk=4096):
        self.__host = host
        self.__port = port

        self.__audio_format = audio_format
        self.__channels = channels
        self.__rate = rate
        self.__frame_chunk = frame_chunk

        self.__sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__audio = pyaudio.PyAudio()

        self.__running = False
        self.__pause = False

        self.__mapping_key = self.key_generation()
    
    def key_generation(self):
        random.seed(85)
        pool = "0123456789abcdef"
        original_pool = list(pool)
        shuffled_pool = list(pool)
        random.shuffle(shuffled_pool)
        monoalpha_key = dict(zip(original_pool, shuffled_pool))
        return monoalpha_key
    
    def encrypt_audio(self,data):
        data = data.hex()
        data = data.translate(data.maketrans(self.__mapping_key))
        data = bytes().fromhex(data)
        return data


    #
    # def __callback(self, in_data, frame_count, time_info, status):
    #     if self.__running:
    #         self.__sending_socket.send(in_data)
    #         return (None, pyaudio.paContinue)
    #     else:
    #         try:
    #             self.__stream.stop_stream()
    #             self.__stream.close()
    #             self.__audio.terminate()
    #             self.__sending_socket.close()
    #         except OSError:
    #             pass # Dirty Solution For Now (Read Overflow)
    #         return (None, pyaudio.paComplete)

    def start_stream(self):
        if self.__running:
            print("Already streaming")
        else:
            self.__running = True
            thread = threading.Thread(target=self.__client_streaming)
            thread.start()

    def stop_stream(self):
        if self.__running:
            self.__running = False
        else:
            print("Client not streaming")
    
    def pause_stream(self):
        if self.__pause:
            print("Already Paused")
        else:
            self.__pause = True
    
    def continue_stream(self):
        if self.__pause:
            self.__pause = False
        else:
            print("Already streaming")

    def __client_streaming(self):
        self.__sending_socket.connect((self.__host, self.__port))
        self.__stream = self.__audio.open(format=self.__audio_format, channels=self.__channels, rate=self.__rate, input=True, frames_per_buffer=self.__frame_chunk)
        while self.__running:
            if self.__pause:
                pass
            else:
                data = self.__stream.read(self.__frame_chunk)
                data = self.encrypt_audio(data)
                self.__sending_socket.send(data)

class AudioReceiver:

    def __init__(self, host, port, slots=8, audio_format=pyaudio.paInt16, channels=1, rate=44100, frame_chunk=4096):
        self.__host = host
        self.__port = port

        self.__slots = slots
        self.__used_slots = 0

        self.__audio_format = audio_format
        self.__channels = channels
        self.__rate = rate
        self.__frame_chunk = frame_chunk

        self.__audio = pyaudio.PyAudio()

        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.bind((self.__host, self.__port))

        self.__block = threading.Lock()
        self.__running = False

        self.__reverse_mapping_key = self.key_generation()
    
    def key_generation(self):
        random.seed(85)
        pool = "0123456789abcdef"
        original_pool = list(pool)
        shuffled_pool = list(pool)
        random.shuffle(shuffled_pool)
        inverse_monoalpha_key = dict(zip(shuffled_pool, original_pool))
        return inverse_monoalpha_key
    
    def decrypt_audio(self,data):
        data = data.hex()
        data = data.translate(data.maketrans(self.__reverse_mapping_key))
        data = bytes().fromhex(data)
        return data

    def start_server(self):
        if self.__running:
            print("Audio server is running already")
        else:
            self.__running = True
            self.__stream = self.__audio.open(format=self.__audio_format, channels=self.__channels, rate=self.__rate, output=True, frames_per_buffer=self.__frame_chunk)
            thread = threading.Thread(target=self.__server_listening)
            thread.start()

    def __server_listening(self):
        self.__server_socket.listen()
        while self.__running:
            self.__block.acquire()
            connection, address = self.__server_socket.accept()
            if self.__used_slots >= self.__slots:
                print("Connection refused! No free slots!")
                connection.close()
                self.__block.release()
                continue
            else:
                self.__used_slots += 1

            self.__block.release()
            thread = threading.Thread(target=self.__client_connection, args=(connection, address,))
            thread.start()

    def __client_connection(self, connection, address):
        while self.__running:
            data = connection.recv(self.__frame_chunk)
            data = self.decrypt_audio(data)
            self.__stream.write(data)

    def stop_server(self):
        if self.__running:
            self.__running = False
            closing_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            closing_connection.connect((self.__host, self.__port))
            closing_connection.close()
            self.__block.acquire()
            self.__server_socket.close()
            self.__block.release()
        else:
            print("Server not running!")


# for public IP Address
# import requests

class ZoomClone:
    def __init__(self,local_ip_address):
        self.local_ip_address = local_ip_address
        self.server = StreamingServer(local_ip_address, 7777)
        self.receiver = AudioReceiver(local_ip_address, 6666)
    
    def start_listening(self):
        t1 = threading.Thread(target=self.server.start_server)
        t2 = threading.Thread(target=self.receiver.start_server)
        t1.start()
        t2.start()
    
    def stop_listening(self):
        t1_ = threading.Thread(target=self.server.stop_server)
        t2_ = threading.Thread(target=self.receiver.stop_server)
        t1_.start()
        t2_.start()
    
    def start_camera_stream(self,client_ip_address):
        self.camera_client = CameraClient(client_ip_address, 9999)
        t3 = threading.Thread(target=self.camera_client.start_stream)
        t3.start()
    
    def stop_camera_stream(self):
        t3_ = threading.Thread(target=self.camera_client.stop_stream)
        t3_.start()

    def start_screen_sharing(self,client_ip_address):
        self.screen_client = ScreenShareClient(client_ip_address, 9999)
        t4 = threading.Thread(target=self.screen_client.start_stream)
        t4.start()
    
    def stop_screen_sharing(self):
        t4_ = threading.Thread(target=self.screen_client.stop_stream)
        t4_.start()
    
    def start_audio_stream(self,client_ip_address):
        self.audio_sender = AudioSender(client_ip_address, 8888)
        t5 = threading.Thread(target=self.audio_sender.start_stream)
        t5.start()
    
    def stop_audio_stream(self):
        t5_ = threading.Thread(target=self.audio_sender.stop_stream)
        t5_.start()
    
    def pause_audio_stream(self):
        t51 = threading.Thread(target=self.audio_sender.pause_stream)
        t51.start()

    def continue_audio_stream(self):
        t51_ = threading.Thread(target=self.audio_sender.continue_stream)
        t51_.start()

local_ip_address = socket.gethostbyname(socket.gethostname())
# local_ip_address = requests.get('https://api.ipify.org').text

zoom = ZoomClone(local_ip_address)

window = tk.Tk()
window.title("Video Call from Device 2")
window.geometry('1000x400')

label_target_ip = tk.Label(window, text="Target IP:",width=50)
label_target_ip.grid(row=0,column=1)

text_target_ip = tk.Text(window,height=1,width=50)
text_target_ip.grid(row=0,column=2)

blank_label1 = tk.Label(window, text="",width=50)
blank_label1.grid(row=1,column=1)

blank_label2 = tk.Label(window, text="",width=50)
blank_label2.grid(row=1,column=2)

btn_listen = tk.Button(window, text="Start Listening", width=50, command= zoom.start_listening)
btn_listen.grid(row=2,column=1)

btn_stop_listen = tk.Button(window, text="Stop Listening", width=50, command= zoom.stop_listening)
btn_stop_listen.grid(row=2,column=2)

blank_label3 = tk.Label(window, text="",width=50)
blank_label3.grid(row=3,column=1)

blank_label4 = tk.Label(window, text="",width=50)
blank_label4.grid(row=3,column=2)

btn_camera = tk.Button(window, text="Start Camera Stream", width=50, command=lambda: zoom.start_camera_stream(text_target_ip.get(1.0,'end-1c')))
btn_camera.grid(row=4,column=1)

btn_stop_camera = tk.Button(window, text="Stop Camera Stream", width=50, command= zoom.stop_camera_stream)
btn_stop_camera.grid(row=4,column=2)

btn_screen = tk.Button(window, text="Start Screen Sharing", width=50, command=lambda: zoom.start_screen_sharing(text_target_ip.get(1.0,'end-1c')))
btn_screen.grid(row=5,column=1)

btn_stop_screen = tk.Button(window, text="Stop Screen Sharing", width=50, command= zoom.stop_screen_sharing)
btn_stop_screen.grid(row=5,column=2)

btn_audio = tk.Button(window, text="Start Audio Stream", width=50, command=lambda: zoom.start_audio_stream(text_target_ip.get(1.0,'end-1c')))
btn_audio.grid(row=6,column=1)

btn_stop_audio = tk.Button(window, text="Stop Audio Stream", width=50, command= zoom.stop_audio_stream)
btn_stop_audio.grid(row=6,column=2)

blank_label5 = tk.Label(window, text="",width=50)
blank_label5.grid(row=7,column=1)

blank_label6 = tk.Label(window, text="",width=50)
blank_label6.grid(row=7,column=2)

btn_pause_audio = tk.Button(window, text="Mute Audio", width=50, command= zoom.pause_audio_stream)
btn_pause_audio.grid(row=8,column=1)

btn_continue_audio = tk.Button(window, text="Unmute Audio", width=50, command= zoom.continue_audio_stream)
btn_continue_audio.grid(row=8,column=2)

window.mainloop()