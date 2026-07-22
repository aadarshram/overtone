#!/usr/bin/env python3
"""Record acoustic channel output from the microphone."""

from __future__ import annotations

import argparse
from pathlib import Path

import sounddevice as sd
from scipy.io.wavfile import write

import _bootstrap  # noqa: F401

from ofdm_dqpsk.config import DEFAULT_CONFIG


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("final_ofdm_rx.wav"),
        help="Output RX WAV path",
    )
    parser.add_argument(
        "--seconds",
        type=float,
        default=17.0,
        help="Recording duration in seconds",
    )
    parser.add_argument(
        "--fs",
        type=int,
        default=DEFAULT_CONFIG.fs,
        help="Sample rate",
    )
    args = parser.parse_args()

    print("Recording...")
    recording = sd.rec(
        int(args.seconds * args.fs),
        samplerate=args.fs,
        channels=1,
    )
    sd.wait()
    print("Finished recording.")
    write(str(args.out), args.fs, recording)
    print(f"Saved to {args.out}")


if __name__ == "__main__":
    main()
