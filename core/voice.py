"""
Cyra-OS Voice System v2
Edge TTS + Google STT with wake word, voice interruption, and status reporting.
"""
import asyncio
import edge_tts
import winsound
import tempfile
import subprocess
import os
from pathlib import Path
import threading
import time
import speech_recognition as sr

VOICE_NAME = "en-US-AriaNeural"
VOICE_NAME_RO = "ro-RO-AlinaNeural"


class VoiceSystem:
    def __init__(self):
        self.speaking = False
        self.listening = False
        self.wake_word_mode = False
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self._stop_listening = None
        self._speak_thread = None
        self._interrupt_event = threading.Event()
        self.error = None
        self._mic_calibrated = False

    def _calibrate_mic(self):
        if self._mic_calibrated:
            return
        try:
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self._mic_calibrated = True
        except Exception as e:
            self.error = f"Mic calibration failed: {e}"

    async def speak(self, text: str, voice: str = None):
        """Speak text. Supports interruption via stop_speaking()."""
        self.speaking = True
        self._interrupt_event.clear()
        tmp_mp3 = None
        tmp_wav = None
        try:
            voice = voice or VOICE_NAME
            communicate = edge_tts.Communicate(text, voice)
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tmp_mp3 = f.name
            await communicate.save(tmp_mp3)

            tmp_wav = tmp_mp3.replace(".mp3", ".wav")
            process = await asyncio.create_subprocess_exec(
                "ffmpeg", "-y", "-i", tmp_mp3, "-acodec", "pcm_s16le",
                "-ar", "22050", "-ac", "1", tmp_wav,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                creationflags=0x08000000
            )
            await process.communicate()

            if Path(tmp_wav).exists():
                # Check for interruption before playing
                if not self._interrupt_event.is_set():
                    winsound.PlaySound(tmp_wav, winsound.SND_FILENAME)
        except Exception as e:
            self.error = f"TTS error: {e}"
        finally:
            self.speaking = False
            for f in [tmp_mp3, tmp_wav]:
                if f and Path(f).exists():
                    try:
                        os.unlink(f)
                    except:
                        pass

    def stop_speaking(self):
        """Interrupt current TTS playback."""
        self._interrupt_event.set()
        self.speaking = False

    def speak_sync(self, text: str, voice: str = None):
        def _target():
            asyncio.run(self.speak(text, voice))
        self._speak_thread = threading.Thread(target=_target, daemon=True)
        self._speak_thread.start()

    def start_listening(self, callback):
        """Start background STT. Supports voice interruption."""
        if self.listening:
            return
        self.listening = True
        self._calibrate_mic()

        def _bg_listener(recognizer, audio):
            try:
                text = recognizer.recognize_google(audio)
                if text:
                    # Voice interruption: stop TTS when user speaks
                    if self.speaking:
                        self.stop_speaking()
                    callback(text)
            except sr.UnknownValueError:
                pass
            except Exception as e:
                self.error = f"STT error: {e}"

        try:
            self._stop_listening = self.recognizer.listen_in_background(
                self.mic, _bg_listener
            )
        except Exception as e:
            self.error = f"Listen start failed: {e}"
            self.listening = False

    def stop_listening(self):
        if self._stop_listening:
            self._stop_listening(wait_for_stop=False)
            self._stop_listening = None
        self.listening = False

    def get_status(self):
        return {
            "speaking": self.speaking,
            "listening": self.listening,
            "wake_word": self.wake_word_mode,
            "error": self.error
        }


voice = VoiceSystem()
