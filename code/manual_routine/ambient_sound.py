import os
import time
import random
import subprocess
import threading
import queue
from pydub import AudioSegment
import pygame
from usb_sound_controller import USB_SoundController

################################################################
# USB Sound Controller for ND Robotics Course
# 3-7-2025
# Professor McLaughlin
################################################################
# class USB_SoundController:
#     def __init__(self, volume=0.7):
#         # Initializes the sound controller.
#         # param volume: Initial volume (0.0 to 1.0)
#         #
#         # Initialize pygame mixer for consistent audio playback.
#         pygame.mixer.pre_init(44100, -16, 2, 512)
#         pygame.init()
#         pygame.mixer.set_num_channels(8)
#         self.volume = volume
#         self.start_time = None
#         self.current_sound = None  # Currently playing sound identifier
#         self.current_channel = None  # Pygame Channel for playback
#         self.sounds = {}  # For pre-loaded sounds (if needed)
#         # Set up a task queue and a worker thread to process audio commands.
#         self.task_queue = queue.Queue()
#         self.stop_event = threading.Event()
#         self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
#         self.worker_thread.start()
# 
#     def _worker_loop(self):
#         # Worker thread loop to process queued tasks sequentially.
#         while not self.stop_event.is_set():
#             try:
#                 # Wait for a task (with timeout so we can check the stop_event periodically)
#                 task, args, kwargs = self.task_queue.get(timeout=0.5)
#                 try:
#                     task(*args, **kwargs)
#                 except Exception as e:
#                     print("Error executing task:", e)
#                 self.task_queue.task_done()
#             except queue.Empty:
#                 continue
# 
#     def _enqueue_task(self, task, *args, **kwargs):
#         # Enqueue a function to be executed by the worker thread.
#         self.task_queue.put((task, args, kwargs))
# 
#     # ----- Audio Playback Functions -----
#     def _convert_mp3_to_wav(self, file_path):
#         # Converts an MP3 file to WAV format for playback.
#         # param file_path: Path to the MP3 file.
#         # return: Path to the WAV file.
#         wav_path = file_path.replace(".mp3", ".wav")
#         if not os.path.exists(wav_path):
#             try:
#                 audio = AudioSegment.from_mp3(file_path)
#                 audio.export(wav_path, format="wav")
#             except Exception as e:
#                 print(f"Error converting MP3 to WAV: {e}")
#         return wav_path
# 
#     def _play_wav(self, file_path):
#         # Loads and plays a WAV file using pygame.
#         # param file_path: Path to the WAV file.
#         if not os.path.exists(file_path):
#             print("Error: WAV file does not exist:", file_path)
#             return
#         try:
#             sound = pygame.mixer.Sound(file_path)
#             sound.set_volume(self.volume)
#             self.current_channel = sound.play()
#             self.start_time = time.time()
#             self.current_sound = file_path
#         except Exception as e:
#             print(f"Error playing WAV file '{file_path}':", e)
# 
#     def play_audio(self, file_path):
#         # Enqueue playing an audio file. If MP3, convert to WAV first.
#         # param file_path: Path to the audio file.
#         self._enqueue_task(self._play_audio_task, file_path)
# 
#     def _play_audio_task(self, file_path):
#         if not os.path.exists(file_path):
#             print("Error: File does not exist:", file_path)
#             return
#         if file_path.lower().endswith(".mp3"):
#             file_path = self._convert_mp3_to_wav(file_path)
#         self._play_wav(file_path)
# 
#     # ----- Text-to-Speech Function -----
#     def play_text_to_speech(self, text):
#         # Enqueue generating speech audio from text using Festival (US SLT HTS)
#         # and play it.
#         # param text: The text to synthesize.
#         self._enqueue_task(self._play_text_to_speech_task, text)
# 
#     def _play_text_to_speech_task(self, text):
#         # Immediately set the Festival voice to US SLT HTS.
#         # voice_command = f"(voice_us_slt_hts)"
#         # subprocess.call(f'echo "{voice_command}" | festival --pipe', shell=True)
#         # Generate TTS audio into a temporary file using text2wave.
#         temp_wav = "temp_tts.wav"
#         command = f'echo "{text}" | text2wave -o {temp_wav}'
#         ret = subprocess.call(command, shell=True)
#         if ret == 0 and os.path.exists(temp_wav):
#             self._play_wav(temp_wav)
#         else:
#             print("Error generating TTS audio with text2wave.")
# 
#     # ----- Control Functions -----
#     def stop_sound(self):
#         # Immediately stops any currently playing sound and purges pending tasks
#         # from the queue.
#         pygame.mixer.stop()
#         self.start_time = None
#         self.current_sound = None
#         # Purge the task queue.
#         with self.task_queue.mutex:
#             self.task_queue.queue.clear()
# 
#     def set_volume(self, volume):
#         # Enqueue setting the volume (0.0 to 1.0) for playback.
#         # param volume: Desired volume level.
#         self._enqueue_task(self._set_volume_task, volume)
# 
#     def _set_volume_task(self, volume):
#         self.volume = max(0.0, min(1.0, volume))
#         # Update volume for pre-loaded sounds if needed.
#         for key, sound in self.sounds.items():
#             sound.set_volume(self.volume)
# 
#     # ----- Close/Cleanup Function -----
#     def close(self):
#         # Clears the task queue, stops the worker thread, and quits pygame.
#         self.stop_event.set()
#         with self.task_queue.mutex:
#             self.task_queue.queue.clear()
#         self.worker_thread.join()
#         pygame.quit()
#         print("USB_SoundController closed gracefully.")

# ---------------- Ambient Sound Routine ---------------- #
class AmbientSoundRoutine:
    def __init__(self, sound_controller, sound_list):
        """
        sound_controller: Instance of USB_SoundController.
        sound_list: List of at least 5 sound file paths.
        """
        self.sound_controller = sound_controller
        self.sound_list = sound_list
        self.running = False  # Controls if the routine is active.
        self.thread = None
        self.lock = threading.Lock()

    def start(self):
        with self.lock:
            if not self.running:
                self.running = True
                # (Re)create and start the thread if not alive.
                self.thread = threading.Thread(target=self._run, daemon=True)
                self.thread.start()
                print("Ambient sound routine started.")

    def stop(self):
        with self.lock:
            if self.running:
                self.running = False
                print("Ambient sound routine suspended.")

    def _run(self):
        while self.running:
#             # Random wait time between 1 and 5 seconds.
#             wait_time = random.uniform(5, 10)
#             time.sleep(wait_time)
#             # Check if still running before playing a sound.
#             if not self.running:
#                 break
#             # Choose a random sound file from the list.
#             sound_file = random.choice(self.sound_list)
#             print(f"Playing: {sound_file}")
#             self.sound_controller.play_audio(sound_file)

            # Choose a random play duration between 5 and 10 seconds.
            play_duration = random.uniform(5, 10)
            
            # Choose a random sound file from the list.
            sound_file = random.choice(self.sound_list)
            print(f"Playing: {sound_file} for {play_duration:.2f} seconds")
            
            # Start playing the sound.
            self.sound_controller.play_audio(sound_file)
            
            # Wait for the random duration.
            time.sleep(play_duration)
            
            # Stop the sound if it's still playing.
            self.sound_controller.stop_sound()

            


# ---------------- PS5 Controller Handling ---------------- #
def initialize_controller():
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
        controller = pygame.joystick.Joystick(0)
        controller.init()
        print(f"Controller '{controller.get_name()}' initialized.")
        return controller
    else:
        print("No PS5 controller detected. Ambient routine control disabled.")
        return None

def process_controller_events(ambient_routine):
    """
    Checks for PS5 controller events.
    In this example, pressing button 0 toggles the ambient routine.
    """
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            # Toggle the ambient routine on button press (assume button 0).
            if event.button == 0:
                if ambient_routine.running:
                    ambient_routine.stop()
                else:
                    ambient_routine.start()

# ---------------- Main Routine ---------------- #
if __name__ == "__main__":
    # Initialize the sound controller.
    sound_ctrl = USB_SoundController(volume=0.7)

    # List of at least 5 different background ambient sounds.
    ambient_sounds = [
        "/home/ndrobotics/code/Pi Only Files /sounds/boxbox.mp3",
        "/home/ndrobotics/code/Pi Only Files /sounds/f1.mp3",
        "/home/ndrobotics/code/Pi Only Files /sounds/italiananthem.mp3",
        "/home/ndrobotics/code/Pi Only Files /sounds/SmoothOperator.mp3",
        "/home/ndrobotics/code/Pi Only Files /sounds/kimisteeringwheel.mp3"
    ]

    # Create the AmbientSoundRoutine instance.
    ambient_routine = AmbientSoundRoutine(sound_ctrl, ambient_sounds)

    # Initialize PS5 controller (if available).
    controller = initialize_controller()

    # Start the ambient routine by default.
    ambient_routine.start()

    try:
        # Main loop polls for controller events to toggle ambient sounds.
        while True:
            process_controller_events(ambient_routine)
            time.sleep(0.1)  # Small delay to avoid busy-waiting.
    except KeyboardInterrupt:
        print("Exiting ambient routine...")
    finally:
        ambient_routine.stop()
        sound_ctrl.close()
