"""Optional AWGN + delay channel simulator (notebook helper)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy.io import wavfile

from .config import DEFAULT_CONFIG, SystemConfig


def simulate_channel(
    tx_file: str | Path,
    rx_file: str | Path,
    snr_db: float = 100.0,
    delay_sec: float = 0.0,
    cfg: SystemConfig = DEFAULT_CONFIG,
) -> None:
    _, tx_sig = wavfile.read(str(tx_file))
    tx_sig = tx_sig.astype(np.float32) / 32768.0

    delay_samples = int(cfg.fs * delay_sec)
    rx_sig = np.concatenate([np.zeros(delay_samples), tx_sig])

    signal_power = np.mean(tx_sig**2)
    noise_power = signal_power / (10 ** (snr_db / 10))
    noise = np.random.normal(0, np.sqrt(noise_power), len(rx_sig))

    rx_noisy = rx_sig + noise
    rx_noisy = rx_noisy / np.max(np.abs(rx_noisy))

    wavfile.write(str(rx_file), cfg.fs, np.int16(rx_noisy * 32767))
    print(
        f"[Channel] Added {delay_sec}s delay and {snr_db}dB AWGN to {rx_file}"
    )
