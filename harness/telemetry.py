"""GPU telemetry for local model runs: background nvidia-smi sampling while a
model works, summarized into peak VRAM, average power, and energy used.
Silently disabled when nvidia-smi is unavailable."""

import shutil
import subprocess
import threading
import time


class GpuSampler:
    def __init__(self, interval_s: float = 2.0):
        self.interval = interval_s
        self._samples: list[tuple[float, float]] = []
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._t0 = 0.0

    @staticmethod
    def available() -> bool:
        return shutil.which("nvidia-smi") is not None

    def _sample_once(self) -> None:
        try:
            out = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used,power.draw",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, encoding="utf-8", timeout=5)
            if out.returncode != 0 or not out.stdout.strip():
                return
            first = out.stdout.strip().splitlines()[0]
            mem_s, power_s = (x.strip() for x in first.split(",", 1))
            self._samples.append((float(mem_s), float(power_s)))
        except (OSError, subprocess.TimeoutExpired, ValueError):
            pass

    def _loop(self) -> None:
        while not self._stop.wait(self.interval):
            self._sample_once()

    def start(self) -> None:
        self._t0 = time.monotonic()
        self._sample_once()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> dict | None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=self.interval + 6)
        duration_s = time.monotonic() - self._t0
        if not self._samples:
            return None
        vram = [s[0] for s in self._samples]
        power = [s[1] for s in self._samples]
        avg_w = sum(power) / len(power)
        return {
            "vram_peak_mb": round(max(vram)),
            "vram_avg_mb": round(sum(vram) / len(vram)),
            "power_avg_w": round(avg_w, 1),
            "power_peak_w": round(max(power), 1),
            "duration_s": round(duration_s, 1),
            "energy_wh": round(avg_w * duration_s / 3600, 3),
            "n_samples": len(self._samples),
        }
