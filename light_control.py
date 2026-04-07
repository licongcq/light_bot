import logging

import requests

log = logging.getLogger(__name__)


class LightController:
    def __init__(self, base_url: str, light_ids: list[str], timeout: float = 5.0):
        self.base_url = base_url
        self.light_ids = light_ids
        self.timeout = timeout

    def _set(self, on: bool):
        payload = {"on": on}
        for light_id in self.light_ids:
            url = self.base_url % light_id
            try:
                resp = requests.put(url, json=payload, timeout=self.timeout, verify=False)
                log.info("Light %s -> on=%s: HTTP %d", light_id, on, resp.status_code)
            except requests.RequestException as e:
                log.error("Failed to set light %s: %s", light_id, e)

    def turn_on(self):
        log.info("Turning lights ON")
        self._set(True)

    def turn_off(self):
        log.info("Turning lights OFF")
        self._set(False)
