"""Zadoff–Chu preamble generation (shared by Tx and Rx)."""

from __future__ import annotations

import numpy as np
import scipy.signal as signal

from .config import DEFAULT_CONFIG, SystemConfig


def zadoff_chu_sequence(length: int, root: int) -> np.ndarray:
    n = np.arange(length)
    return np.exp(-1j * np.pi * root * n * (n + 1) / length)


def build_zc_preamble_spectrum(
    cfg: SystemConfig = DEFAULT_CONFIG,
) -> tuple[np.ndarray, list[int]]:
    """Frequency-domain ZC preamble with conjugate symmetry for a real IFFT."""
    zc_seq = zadoff_chu_sequence(cfg.zc_length, cfg.zc_root)
    X_preamble = np.zeros(cfg.n_samples, dtype=complex)
    active_bins: list[int] = []

    for i in range(cfg.zc_length):
        bin_idx = cfg.start_bin + (i * cfg.bin_spacing)
        X_preamble[bin_idx] = zc_seq[i]
        X_preamble[-bin_idx] = np.conj(zc_seq[i])
        active_bins.append(bin_idx)
        active_bins.append(-bin_idx)

    return X_preamble, active_bins


def build_zc_preamble_waveform(
    cfg: SystemConfig = DEFAULT_CONFIG,
    apply_window: bool = True,
) -> tuple[np.ndarray, np.ndarray, list[int]]:
    """
    Return (time-domain CP+body preamble, frequency-domain preamble, active bins).
    """
    X_preamble, active_bins = build_zc_preamble_spectrum(cfg)
    x_t = np.fft.ifft(X_preamble).real
    x_cp = np.concatenate([x_t[-cfg.cp_samples :], x_t])

    if apply_window:
        x_cp = x_cp * signal.windows.tukey(len(x_cp), alpha=cfg.tx_tukey_alpha)

    return x_cp, X_preamble, active_bins
