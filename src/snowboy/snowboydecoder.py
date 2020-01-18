#!/usr/bin/env python

import collections
import pyaudio
import snowboydetect
import time
import wave
import os
import sys
from ctypes import CFUNCTYPE, c_char_p, c_int, cdll
from contextlib import contextmanager


TOP_DIR = os.path.dirname(os.path.abspath(__file__))
APP_PATH = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), os.pardir))
sys.path.append(os.path.join(APP_PATH,"util/"))

try:
    from config_helper import *
except ImportError:
    raise

RESOURCE_FILE = os.path.join(TOP_DIR, "resources/common.res")
DETECT_DING = os.path.join(TOP_DIR, "resources/ding.wav")
DETECT_DONG = os.path.join(TOP_DIR, "resources/dong.wav")

def py_error_handler(filename, line, function, err, fmt):
    print("snowboydecoder err-->",err)

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def no_alsa_error():
    try:
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield
        pass

class RingBuffer(object):
    """Ring buffer to hold audio from PortAudio"""

    def __init__(self, size=4096):
        self._buf = collections.deque(maxlen=size)

    def extend(self, data):
        """Adds data to the end of buffer"""
        self._buf.extend(data)

    def get(self):
        """Retrieves data from the beginning of buffer and clears it"""
        tmp = bytes(bytearray(self._buf))
        self._buf.clear()
        return tmp


def play_audio_file(fname=DETECT_DING):
    """Simple callback function to play a wave file. By default it plays
    a Ding sound.

    :param str fname: wave file name
    :return: None
    """
    ding_wav = wave.open(fname, 'rb')
    ding_data = ding_wav.readframes(ding_wav.getnframes())
    with no_alsa_error():
        audio = pyaudio.PyAudio()
    stream_out = audio.open(
        format=audio.get_format_from_width(ding_wav.getsampwidth()),
        channels=ding_wav.getnchannels(),
        rate=ding_wav.getframerate(), input=False, output=True)
    stream_out.start_stream()
    stream_out.write(ding_data)
    time.sleep(0.2)
    stream_out.stop_stream()
    stream_out.close()
    audio.terminate()


class ActiveListener(object):
    """ Active Listening with VAD """
    def __init__(self, decoder_model,
                 resource=RESOURCE_FILE):

        self.recordedData = []
        model_str = ",".join(decoder_model)
        self.detector = snowboydetect.SnowboyDetect(
            resource_filename=resource.encode(), model_str=model_str.encode())
        self.ring_buffer = RingBuffer(
            self.detector.NumChannels() * self.detector.SampleRate() * 5)

    def listen(self, interrupt_check=lambda: False, sleep_time=0.03, silent_count_threshold=15, recording_timeout=100):
        """
        :param interrupt_check: a function that returns True if the main loop
                                needs to stop.
        :param silent_count_threshold: indicates how long silence must be heard
                                       to mark the end of a phrase that is
                                       being recorded.
        :param float sleep_time: how much time in second every loop waits.
        :param recording_timeout: limits the maximum length of a recording.
        :return: recorded file path
        """


        self._running = True

        def audio_callback(in_data, frame_count, time_info, status):
            self.ring_buffer.extend(in_data)
            play_data = chr(0) * len(in_data)
            return play_data, pyaudio.paContinue

        with no_alsa_error():            
            self.audio = pyaudio.PyAudio()
        try:
            RESPEAKER_INDEX = 2 # refer to input device id
            self.stream_in = self.audio.open(
                input=True, output=False,
                format=self.audio.get_format_from_width(
                    self.detector.BitsPerSample() / 8),
                channels=self.detector.NumChannels(),
                rate=self.detector.SampleRate(),
                frames_per_buffer=2048,
                input_device_index=RESPEAKER_INDEX,
                stream_callback=audio_callback
                )
        except Exception as e:
            return 

        print('audio stream opened')

        if interrupt_check():
            print("detect voice return")
            return

        silentCount = 0
        recordingCount = 0

        print("begin activeListen loop")
        
        while self._running is True:

            if interrupt_check():
                print("detect voice break")
                break
            data = self.ring_buffer.get()
            if len(data) == 0:
                time.sleep(sleep_time)
                continue
            
            status = self.detector.RunDetection(data)

            print("status:",status)
            if status == -1:
                #logger.warning("Error initializing streams or reading audio data")
		        pass
                
            stopRecording = False

            if recordingCount > int(recording_timeout):
                stopRecording = True
            elif status == -2: #silence found
                if silentCount > int(silent_count_threshold):
                    stopRecording = True
                else:
                    silentCount = silentCount + 1
            elif status == 0: #voice found
                silentCount = 0

            if stopRecording == True:
                return self.saveMessage()

            recordingCount = recordingCount + 1
            self.recordedData.append(data)

        print("finished.")


    def saveMessage(self):
        """
        Save the message stored in self.recordedData to a timestamped file.
        """
        filename = os.path.join(config.TEMP_PATH, 'output' + str(int(time.time())) + '.wav')
        data = b''.join(self.recordedData)

        #use wave to save data
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.detector.NumChannels())
        wf.setsampwidth(self.audio.get_sample_size(
            self.audio.get_format_from_width(self.detector.BitsPerSample() / 8)))
        wf.setframerate(self.detector.SampleRate())
        wf.writeframes(data)
        wf.close()
        print("finished saving: " + filename)

        self.stream_in.stop_stream()
        self.stream_in.close()
        self.audio.terminate()
        
        return filename
    
    


class HotwordDetector(object):
    """
    Snowboy decoder to detect whether a keyword specified by `decoder_model`
    exists in a microphone input stream.

    :param decoder_model: decoder model file path, a string or a list of strings
    :param resource: resource file path.
    :param sensitivity: decoder sensitivity, a float of a list of floats.
                              The bigger the value, the more senstive the
                              decoder. If an empty list is provided, then the
                              default sensitivity in the model will be used.
    :param audio_gain: multiply input volume by this factor.
    :param apply_frontend: applies the frontend processing algorithm if True.
    """

    def __init__(self, decoder_model,
                 resource=RESOURCE_FILE,
                 sensitivity=[],
                 audio_gain=1,
                 apply_frontend=False):

        self._running = False

        tm = type(decoder_model)
        ts = type(sensitivity)
        if tm is not list:
            decoder_model = [decoder_model]
        if ts is not list:
            sensitivity = [sensitivity]
        model_str = ",".join(decoder_model)

        self.detector = snowboydetect.SnowboyDetect(
            resource_filename=resource.encode(), model_str=model_str.encode())
        self.detector.SetAudioGain(audio_gain)
        self.detector.ApplyFrontend(apply_frontend)
        self.num_hotwords = self.detector.NumHotwords()

        if len(decoder_model) > 1 and len(sensitivity) == 1:
            sensitivity = sensitivity * self.num_hotwords
        if len(sensitivity) != 0:
            assert self.num_hotwords == len(sensitivity), \
                "number of hotwords in decoder_model (%d) and sensitivity " \
                "(%d) does not match" % (self.num_hotwords, len(sensitivity))
        sensitivity_str = ",".join([str(t) for t in sensitivity])
        if len(sensitivity) != 0:
            self.detector.SetSensitivity(sensitivity_str.encode())        

        self.ring_buffer = RingBuffer(
            self.detector.NumChannels() * self.detector.SampleRate() * 5)

    def start(self, detected_callback=play_audio_file,
              interrupt_check=lambda: False,
              sleep_time=0.03,
              audio_recorder_callback=None,
              silent_count_threshold=15,
              recording_timeout=100,
              active_passive_timeout=200,passive_callback = None
              ):
        """
        Start the voice detector. For every `sleep_time` second it checks the
        audio buffer for triggering keywords. If detected, then call
        corresponding function in `detected_callback`, which can be a single
        function (single model) or a list of callback functions (multiple
        models). Every loop it also calls `interrupt_check` -- if it returns
        True, then breaks from the loop and return.

        :param detected_callback: a function or list of functions. The number of
                                  items must match the number of models in
                                  `decoder_model`.
        :param interrupt_check: a function that returns True if the main loop
                                needs to stop.
        :param float sleep_time: how much time in second every loop waits.
        :param audio_recorder_callback: if specified, this will be called after
                                        a keyword has been spoken and after the
                                        phrase immediately after the keyword has
                                        been recorded. The function will be
                                        passed the name of the file where the
                                        phrase was recorded.
        :param silent_count_threshold: indicates how long silence must be heard
                                       to mark the end of a phrase that is
                                       being recorded.
        :param recording_timeout: limits the maximum length of a recording.
        :active_passive_timeout:over active_passive_timeout*sleep_time state will from active change passive
        :return: None
        """
        self._running = True

        def audio_callback(in_data, frame_count, time_info, status):
            self.ring_buffer.extend(in_data)
            play_data = chr(0) * len(in_data)
            return play_data, pyaudio.paContinue

        with no_alsa_error():
            self.audio = pyaudio.PyAudio()
        RESPEAKER_INDEX = 2
        self.stream_in = self.audio.open(
            input=True, output=False,
            format=self.audio.get_format_from_width(
                self.detector.BitsPerSample() / 8),
            channels=self.detector.NumChannels(),
            rate=self.detector.SampleRate(),
            frames_per_buffer=2048,
            input_device_index=RESPEAKER_INDEX,
            stream_callback=audio_callback
            )

        if interrupt_check():
            print("detect voice return")
            return

        tc = type(detected_callback)
        if tc is not list:
            detected_callback = [detected_callback]
        if len(detected_callback) == 1 and self.num_hotwords > 1:
            detected_callback *= self.num_hotwords

        assert self.num_hotwords == len(detected_callback), \
            "Error: hotwords in your models (%d) do not match the number of " \
            "callbacks (%d)" % (self.num_hotwords, len(detected_callback))

        print("detecting...")

        state = "PASSIVE"
        while self._running is True:            
            if interrupt_check():
                print("detect voice break")
                break
            data = self.ring_buffer.get()
            if len(data) == 0:
                time.sleep(sleep_time)
                continue

            status = self.detector.RunDetection(data)
            print("status-->:",status)
            print("state-->:",state)
            if status == -1:
                print("Error initializing streams or reading audio data")
                pass

            #small state machine to handle recording of phrase after keyword
            if state == "PASSIVE":
                print("coming state PASSIVE-->:",state)
                if status > 0: #key word found
                    self.recordedData = []
                    self.recordedData.append(data)
                    silentCount = 0
                    recordingCount = 0
                    recording_has_voice = True
                    message = "Keyword " + str(status) + " detected at time: "
                    message += time.strftime("%Y-%m-%d %H:%M:%S",
                                         time.localtime(time.time()))
                    print(message)
                    callback = detected_callback[status-1]                    
                    if callback is not None:
                        callback()

                    if audio_recorder_callback is not None and status == 1:
                        state = "ACTIVE"
                    continue

            elif state == "ACTIVE":
                stopRecording = False
                if recordingCount > int(recording_timeout):
                    stopRecording = True
                elif status == -2: #silence found
                    print("type(silent_count_threshold)",type(silent_count_threshold))
                    if silentCount > int(silent_count_threshold):
                        stopRecording = True
                    else:
                        silentCount = silentCount + 1
                elif status == 0: #voice found
                    silentCount = 0
                    recording_has_voice = True
                print('silentCount > silent_count_threshold',silentCount > int(silent_count_threshold))
                print("silentCount:",silentCount)
                print("silent_count_threshold:",silent_count_threshold)
                print("stopRecording:",stopRecording)
                print("recordingCount:",recordingCount)
                print("recording_timeout:",recording_timeout)
                print("recordingCount > int(active_passive_timeout):",recordingCount > int(active_passive_timeout))
                if recordingCount > int(active_passive_timeout):
                    state = "PASSIVE"
                    if passive_callback is not None:
                        passive_callback()
                    continue
                if stopRecording == True:
                    #print("self.recordedData-->",self.recordedData)
                    if recording_has_voice:
                        fname = self.saveMessage()
                        audio_recorder_callback(fname)
                        #state = "PASSIVE" 
                        #donot change state ,but reset silentCount and   recordingCount by liugang
                        recording_has_voice = False
                        stopRecording = False
                        self.recordedData = []         
                        silentCount = 0
                        recordingCount = 0        
                        continue

                recordingCount = recordingCount + 1
                self.recordedData.append(data)                

        print("finished.")


    def saveMessage(self):
        """
        Save the message stored in self.recordedData to a timestamped file.
        """
        filename = os.path.join(config.TEMP_PATH, 'output' + str(int(time.time())) + '.wav')
        data = b''.join(self.recordedData)

        #use wave to save data
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.detector.NumChannels())
        wf.setsampwidth(self.audio.get_sample_size(
            self.audio.get_format_from_width(
                self.detector.BitsPerSample() / 8)))
        wf.setframerate(self.detector.SampleRate())
        wf.writeframes(data)
        wf.close()
        print("finished saving: " + filename)
        return filename

    def terminate(self):
        """
        Terminate audio stream. Users can call start() again to detect.
        :return: None
        """
        if self._running:
            self.stream_in.stop_stream()
            self.stream_in.close()
            self.audio.terminate()
            self._running = False
