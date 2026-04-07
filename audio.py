import logging

import numpy as np
import sounddevice as sd

log = logging.getLogger(__name__)


def _find_device(name_hint: str, fallback_index: int) -> int:
    if name_hint:
        for device in sd.query_devices():
            if name_hint.lower() in device["name"].lower() and device["max_input_channels"] > 0:
                log.info("Using audio device %d: %s", device["index"], device["name"])
                return device["index"]
        log.warning("No input device matching '%s' found, falling back to device %d", name_hint, fallback_index)
    log.info("Using audio device %d: %s", fallback_index, sd.query_devices(fallback_index)["name"])
    return fallback_index


class AudioStream:
    def __init__(
        self,
        vosk_sample_rate: int = 16000,
        device_sample_rate: int = 48000,
        block_duration_ms: int = 200,
        device_name: str = "USB",
        device: int = 0,
    ):
        self.vosk_sample_rate = vosk_sample_rate
        self.device_sample_rate = device_sample_rate
        # Simple decimation is sufficient for speech: aliasing only affects
        # frequencies above Nyquist of target rate (>8kHz), well outside speech range
        self.ratio = device_sample_rate // vosk_sample_rate
        self.capture_block_size = int(device_sample_rate * block_duration_ms / 1000)
        self.device_index = _find_device(device_name, device)
        self.stream = None

    def __enter__(self):
        self.stream = sd.RawInputStream(
            samplerate=self.device_sample_rate,
            blocksize=self.capture_block_size,
            device=self.device_index,
            channels=1,
            dtype="int16",
        )
        self.stream.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.stream:
            self.stream.stop()
            self.stream.close()

    def read_block(self) -> bytes:
        data, _ = self.stream.read(self.capture_block_size)
        samples = np.frombuffer(bytes(data), dtype=np.int16)
        return samples[:: self.ratio].tobytes()
