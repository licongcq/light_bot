#!/usr/bin/env python3
import logging
import time
from pathlib import Path

import yaml

from audio import AudioStream
from light_control import LightController
from recognizer import VoskRecognizer

log = logging.getLogger("light_bot")


def load_config(path: str = "config.yaml") -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def setup_logging(level: str):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def main():
    config = load_config()
    setup_logging(config.get("log_level", "INFO"))

    cmd_on = config["command_on"]
    cmd_off = config["command_off"]
    sample_rate = config.get("sample_rate", 16000)
    device_sample_rate = config.get("device_sample_rate", 48000)
    block_duration_ms = config.get("block_duration_ms", 500)
    cooldown = config.get("cooldown_sec", 1)
    device_name = config.get("device_name", "USB")
    device = config.get("device", 0)

    model_path = config["model_path"]
    if not Path(model_path).is_absolute():
        model_path = str(Path(__file__).parent / model_path)

    grammar = [cmd_on, cmd_off, "[unk]"]
    recognizer = VoskRecognizer(model_path, sample_rate, grammar)
    lights = LightController(config["light_base_url"], config["light_ids"])

    log.info("Light bot started. On: '%s', Off: '%s'", cmd_on, cmd_off)

    with AudioStream(sample_rate, device_sample_rate, block_duration_ms, device_name, device) as stream:
        while True:
            audio_block = stream.read_block()
            text = recognizer.feed(audio_block)

            if text is None:
                continue

            log.info("Recognized: '%s'", text)

            if cmd_on in text:
                lights.turn_on()
                time.sleep(cooldown)
            elif cmd_off in text:
                lights.turn_off()
                time.sleep(cooldown)


if __name__ == "__main__":
    main()
