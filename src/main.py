#!/usr/bin/env python3
import threading
import time
import random
import math
import queue
import os
import sys

# ============================================================
#  Utility: Dummy CPU + Memory Load
# ============================================================

def cpu_load(duration_ms=40):
    """Burn CPU cycles for a fixed duration."""
    end = time.time() + (duration_ms / 1000.0)
    x = 0.0
    while time.time() < end:
        x += math.sin(random.random())
    return x

def memory_load(size_kb=256):
    """Allocate temporary memory to simulate load."""
    return bytearray(size_kb * 1024)


# ============================================================
#  Base Module Class
# ============================================================

class BaseModule(threading.Thread):
    def __init__(self, name, interval=1.0):
        super().__init__(daemon=True)
        self.name = name
        self.interval = interval
        self.running = False
        self.last_output = None

    def run(self):
        self.running = True
        print(f"[{self.name}] started")

        while self.running:
            start = time.time()

            # Simulate CPU + memory usage
            cpu_load(30)
            memory_load(128)

            # Module-specific work
            self.last_output = self.step()

            # Maintain interval
            elapsed = time.time() - start
            sleep_time = max(0.0, self.interval - elapsed)
            time.sleep(sleep_time)

        print(f"[{self.name}] stopped")

    def stop(self):
        self.running = False

    def step(self):
        """Override in subclass."""
        return None


# ============================================================
#  QHY Camera Controller Module
# ============================================================

class CameraModule(BaseModule):
    def step(self):
        # Dummy camera frame metadata
        frame = {
            "width": 5496,
            "height": 3672,
            "bit_depth": 16,
            "sensor_id": 1,
            "temperature": random.uniform(-10, 20),
            "gain": random.uniform(0, 20),
            "exposure_us": random.randint(5000, 200000),
            "timestamp": time.time()
        }

        # Simulate RAW frame generation
        cpu_load(50)
        memory_load(1024)

        print(f"[camera] frame_id={frame['timestamp']}")
        return frame


# ============================================================
#  CV Pipeline Module (GMM + classical methods)
# ============================================================

class CvPipelineModule(BaseModule):
    def __init__(self, name, interval=0.5):
        super().__init__(name, interval)
        self.frame_queue = queue.Queue(maxsize=5)

    def push_frame(self, frame):
        """Camera module pushes frames here."""
        try:
            self.frame_queue.put_nowait(frame)
        except queue.Full:
            pass  # drop frame

    def step(self):
        if self.frame_queue.empty():
            return None

        frame = self.frame_queue.get()

        # Simulate CV pipeline load
        cpu_load(80)
        memory_load(2048)

        # Dummy event list (GMM + DoG + MHI etc.)
        num_events = random.randint(0, 5)
        events = [
            {
                "event_id": f"E{random.randint(1000,9999)}",
                "x": random.uniform(0, frame["width"]),
                "y": random.uniform(0, frame["height"]),
                "score": random.uniform(0.1, 0.99),
                "type": random.choice(["motion", "blob", "track"])
            }
            for _ in range(num_events)
        ]

        print(f"[cv] events={num_events}")
        return events


# ============================================================
#  TinyML Module (NPU inference)
# ============================================================

class TinyMlModule(BaseModule):
    def __init__(self, name, interval=0.5):
        super().__init__(name, interval)
        self.event_queue = queue.Queue(maxsize=10)

    def push_events(self, events):
        try:
            self.event_queue.put_nowait(events)
        except queue.Full:
            pass

    def step(self):
        if self.event_queue.empty():
            return None

        events = self.event_queue.get()

        # Simulate NPU inference load
        cpu_load(20)
        memory_load(512)

        # Dummy classification results
        classified = [
            {
                "event_id": e["event_id"],
                "label": random.choice(["aircraft", "bird", "satellite", "unknown"]),
                "confidence": random.uniform(0.5, 0.99)
            }
            for e in events
        ]

        print(f"[tinyml] classified={len(classified)}")
        return classified


# ============================================================
#  Orchestrator
# ============================================================

class Orchestrator:
    def __init__(self):
        self.camera = CameraModule("camera", interval=1.0)
        self.cv = CvPipelineModule("cv", interval=0.5)
        self.tinyml = TinyMlModule("tinyml", interval=0.5)

        self.modules = [self.camera, self.cv, self.tinyml]

    def start(self):
        print("[orchestrator] starting modules")
        for m in self.modules:
            m.start()

        # Main orchestrator loop
        threading.Thread(target=self.loop, daemon=True).start()

    def loop(self):
        while True:
            # Connect camera ? CV pipeline
            if self.camera.last_output:
                self.cv.push_frame(self.camera.last_output)

            # Connect CV pipeline ? TinyML
            if self.cv.last_output:
                self.tinyml.push_events(self.cv.last_output)

            time.sleep(0.1)

    def stop(self):
        print("[orchestrator] stopping modules")
        for m in self.modules:
            m.stop()

        for m in self.modules:
            m.join()

    def run(self):
        self.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[orchestrator] shutdown requested")
            self.stop()


# ============================================================
#  Main
# ============================================================

if __name__ == "__main__":
    orch = Orchestrator()
    orch.run()
