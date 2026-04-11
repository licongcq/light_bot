import json
import logging

from vosk import Model, KaldiRecognizer, SetLogLevel

log = logging.getLogger(__name__)


class VoskRecognizer:
    def __init__(self, model_path: str, sample_rate: int, grammar: list[str],
                 min_confidence: float = 0.5):
        SetLogLevel(-1)
        log.info("Loading Vosk model from %s", model_path)
        self.model = Model(model_path)
        grammar_json = json.dumps(grammar, ensure_ascii=False)
        self.recognizer = KaldiRecognizer(self.model, sample_rate, grammar_json)
        self.recognizer.SetWords(True)
        self.min_confidence = min_confidence
        log.info("Recognizer ready with grammar: %s, min_confidence: %.2f",
                 grammar, min_confidence)

    def feed(self, audio_block: bytes) -> str | None:
        if self.recognizer.AcceptWaveform(audio_block):
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "").strip()
            if not text or text == "[unk]":
                return None

            words = result.get("result", [])
            if words:
                avg_conf = sum(w["conf"] for w in words) / len(words)
                if avg_conf < self.min_confidence:
                    log.debug("Rejected '%s' (avg_conf=%.2f < %.2f)",
                              text, avg_conf, self.min_confidence)
                    return None
                log.debug("Accepted '%s' (avg_conf=%.2f)", text, avg_conf)

            return text
        return None
