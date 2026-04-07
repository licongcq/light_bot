import json
import logging

from vosk import Model, KaldiRecognizer, SetLogLevel

log = logging.getLogger(__name__)


class VoskRecognizer:
    def __init__(self, model_path: str, sample_rate: int, grammar: list[str]):
        SetLogLevel(-1)
        log.info("Loading Vosk model from %s", model_path)
        self.model = Model(model_path)
        grammar_json = json.dumps(grammar, ensure_ascii=False)
        self.recognizer = KaldiRecognizer(self.model, sample_rate, grammar_json)
        log.info("Recognizer ready with grammar: %s", grammar)

    def feed(self, audio_block: bytes) -> str | None:
        if self.recognizer.AcceptWaveform(audio_block):
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                return text
        return None
