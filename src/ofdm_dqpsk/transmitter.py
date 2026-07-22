"""OFDM-DQPSK transmitter."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import scipy.signal as signal
from scipy.io import wavfile

from .config import DEFAULT_CONFIG, SystemConfig
from .preamble import build_zc_preamble_waveform


def generate_transmitter(
    original_data: np.ndarray,
    filename: str | Path = "final_ofdm_tx.wav",
    cfg: SystemConfig = DEFAULT_CONFIG,
) -> np.ndarray:
    """
    Build the full TX packet (silence + ZC preamble + reference + data) and write WAV.

    Returns the peak-normalized float waveform.
    """
    tx_signal: list[float] = []

    x_preamble_cp, _, _ = build_zc_preamble_waveform(cfg, apply_window=True)
    tx_signal.extend(x_preamble_cp)

    # Prepend all-zero reference symbol for differential encoding
    all_bit_rows = np.vstack(
        [
            np.zeros((1, cfg.num_bit_cols), dtype=int),
            original_data,
        ]
    )

    sym_window = signal.windows.tukey(
        cfg.total_sym_samples, alpha=cfg.tx_tukey_alpha
    )
    current_data_phases = np.zeros(cfg.num_data_bins)

    for row_bits in all_bit_rows:
        X_f = np.zeros(cfg.n_samples, dtype=complex)

        for p_idx in cfg.pilot_indices:
            bin_idx = cfg.start_bin + (p_idx * cfg.bin_spacing)
            X_f[bin_idx] = 1.0
            X_f[-bin_idx] = 1.0

        for sc in range(cfg.num_data_bins):
            b0 = int(row_bits[sc * 2])
            b1 = int(row_bits[sc * 2 + 1])
            delta_phase = cfg.qpsk_phase_map[(b0, b1)]
            current_data_phases[sc] = (
                current_data_phases[sc] + delta_phase
            ) % (2 * np.pi)

            bin_idx = cfg.start_bin + (cfg.data_indices[sc] * cfg.bin_spacing)
            complex_val = np.exp(1j * current_data_phases[sc])
            X_f[bin_idx] = complex_val
            X_f[-bin_idx] = np.conj(complex_val)

        x_t = np.fft.ifft(X_f).real
        x_t_cp = np.concatenate([x_t[-cfg.cp_samples :], x_t])
        tx_signal.extend(x_t_cp * sym_window)

    silence = np.zeros(int(cfg.fs * cfg.silence_sec))
    tx_signal_arr = np.concatenate([silence, np.asarray(tx_signal), silence])
    tx_signal_norm = tx_signal_arr / np.max(np.abs(tx_signal_arr))

    wavfile.write(
        str(filename),
        cfg.fs,
        np.int16(tx_signal_norm * 32767),
    )
    print(
        f"[Transmitter] Generated {filename} "
        f"({len(tx_signal_norm) / cfg.fs:.2f}s)"
    )
    return tx_signal_norm
