"""OFDM-DQPSK receiver: sync, CFO, differential decode, BER."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.signal as signal
from scipy.io import wavfile

from .config import DEFAULT_CONFIG, SystemConfig
from .plotting import plot_constellation, plot_phase_histogram
from .preamble import build_zc_preamble_waveform


@dataclass
class ReceiverResult:
    recovered_bits: np.ndarray
    diff_symbols: np.ndarray
    ber: float
    bit_errors: int
    total_bits: int
    cfo_hz: float
    phase_drift_per_symbol: float
    preamble_peak_idx: int
    h_est: np.ndarray


def run_receiver(
    rx_file: str | Path,
    original_data: np.ndarray,
    cfg: SystemConfig = DEFAULT_CONFIG,
    *,
    plot: bool = True,
    save_rx_bits: str | Path | None = "rx_bits.csv",
    constellation_path: str | Path | None = None,
    histogram_path: str | Path | None = None,
) -> ReceiverResult:
    _, rx_sig = wavfile.read(str(rx_file))
    rx_sig = rx_sig.astype(np.float32) / 32768.0

    local_preamble_cp, X_preamble, active_bins = build_zc_preamble_waveform(
        cfg, apply_window=True
    )

    # Frame synchronization via matched-filter correlation
    correlation = signal.fftconvolve(
        rx_sig,
        local_preamble_cp[::-1],
        mode="valid",
    )
    peak_idx = int(np.argmax(np.abs(correlation)))
    preamble_start_idx = peak_idx
    ref_symbol_start_idx = peak_idx + len(local_preamble_cp)
    print(f"[Receiver] Preamble found at sample {peak_idx}")

    # Channel estimation from preamble (computed; DQPSK path does not equalize)
    preamble_rx = rx_sig[
        preamble_start_idx + cfg.cp_samples : preamble_start_idx
        + cfg.total_sym_samples
    ]
    rx_window = signal.windows.tukey(cfg.n_samples, alpha=cfg.rx_tukey_alpha)
    rx_window /= np.sqrt(np.mean(rx_window**2))
    preamble_rx = preamble_rx * rx_window
    Y_preamble = np.fft.fft(preamble_rx)

    H_est = np.ones(cfg.n_samples, dtype=complex)
    eps = 1e-12
    for b in active_bins:
        H_est[b] = Y_preamble[b] / (X_preamble[b] + eps)
    print("[Receiver] Channel estimated from preamble")

    num_expected_symbols = original_data.shape[0] + 1  # + reference symbol

    # Pass 1: CFO from pilot-B phase slope
    pilot_a_phases_raw: list[float] = []
    pilot_b_phases_raw: list[float] = []

    for sym_idx in range(num_expected_symbols):
        start_idx = ref_symbol_start_idx + (sym_idx * cfg.total_sym_samples)
        end_idx = start_idx + cfg.total_sym_samples
        if end_idx > len(rx_sig):
            print(f"ERROR: Audio cuts off at Symbol {sym_idx}.")
            break

        core_audio = rx_sig[start_idx + cfg.cp_samples : end_idx]
        X_rx = np.fft.fft(core_audio)

        bin_a = cfg.start_bin + (cfg.pilot_indices[0] * cfg.bin_spacing)
        bin_b = cfg.start_bin + (cfg.pilot_indices[1] * cfg.bin_spacing)
        pilot_a_phases_raw.append(np.angle(X_rx[bin_a]))
        pilot_b_phases_raw.append(np.angle(X_rx[bin_b]))

    pilot_b_phases = np.unwrap(pilot_b_phases_raw)
    sym_indices = np.arange(len(pilot_b_phases))
    slope, _intercept = np.polyfit(sym_indices, pilot_b_phases, 1)
    cfo_hz = float(slope / (2 * np.pi * cfg.t_sym))

    print(f"[CFO] Estimated phase drift per symbol: {slope:.4f} rad")
    print(f"[CFO] Estimated CFO: {cfo_hz:.4f} Hz")

    # Pass 2: extract data subcarriers with bulk CFO correction
    extracted_symbols = np.zeros(
        (num_expected_symbols, cfg.num_data_bins), dtype=complex
    )
    for sym_idx in range(num_expected_symbols):
        start_idx = ref_symbol_start_idx + (sym_idx * cfg.total_sym_samples)
        end_idx = start_idx + cfg.total_sym_samples
        if end_idx > len(rx_sig):
            break

        core_audio = rx_sig[start_idx + cfg.cp_samples : end_idx]
        X_rx = np.fft.fft(core_audio)
        predicted_phase_drift = slope * sym_idx
        X_rx_corrected = X_rx * np.exp(-1j * predicted_phase_drift)

        for i, d_idx in enumerate(cfg.data_indices):
            bin_idx = cfg.start_bin + (d_idx * cfg.bin_spacing)
            extracted_symbols[sym_idx, i] = X_rx_corrected[bin_idx]

    # Differential decode
    diff_symbols = extracted_symbols[1:] * np.conj(extracted_symbols[:-1])
    diff_angles = np.angle(diff_symbols) % (2 * np.pi)

    candidates = np.array([0, np.pi / 2, np.pi, 3 * np.pi / 2])
    dist = np.abs(
        diff_angles[:, :, np.newaxis] - candidates[np.newaxis, np.newaxis, :]
    )
    dist = np.minimum(dist, 2 * np.pi - dist)
    chosen_idx = np.argmin(dist, axis=-1)

    num_data_syms = chosen_idx.shape[0]
    recovered_bits = np.zeros((num_data_syms, cfg.num_bit_cols), dtype=int)
    for sym in range(num_data_syms):
        for sc in range(cfg.num_data_bins):
            b0, b1 = cfg.idx_to_dibit[int(chosen_idx[sym, sc])]
            recovered_bits[sym, sc * 2] = b0
            recovered_bits[sym, sc * 2 + 1] = b1

    errors = int(np.sum(recovered_bits != original_data[:num_data_syms]))
    total_bits = int(original_data[:num_data_syms].size)
    ber = errors / total_bits

    print()
    print("============================")
    print("DQPSK RESULTS")
    print("============================")
    print(f"Total Bits : {total_bits}")
    print(f"Bit Errors : {errors}")
    print(f"BER        : {ber:.6f}")
    print("============================")

    if plot or constellation_path is not None:
        plot_constellation(
            diff_symbols,
            original_data,
            cfg=cfg,
            save_path=constellation_path,
            show=plot,
        )
    if plot or histogram_path is not None:
        plot_phase_histogram(
            diff_symbols,
            save_path=histogram_path,
            show=plot,
        )

    rx_bits = recovered_bits.flatten().astype(np.uint8)[: cfg.num_bits]
    tx_bits = original_data.ravel()
    n = min(len(tx_bits), len(rx_bits))
    tx_bits = tx_bits[:n]
    rx_bits = rx_bits[:n]
    trunc_errors = int(np.sum(tx_bits != rx_bits))
    trunc_ber = trunc_errors / n

    print("TX bits:", len(tx_bits))
    print("RX bits:", len(rx_bits))
    print("Compared:", n)
    print("Errors:", trunc_errors)
    print("BER:", trunc_ber)

    if save_rx_bits is not None:
        pd.DataFrame(rx_bits).to_csv(save_rx_bits, header=False, index=False)
        print(f"Saved {save_rx_bits}; length = {len(rx_bits)}")

    return ReceiverResult(
        recovered_bits=recovered_bits,
        diff_symbols=diff_symbols,
        ber=trunc_ber,
        bit_errors=trunc_errors,
        total_bits=n,
        cfo_hz=cfo_hz,
        phase_drift_per_symbol=float(slope),
        preamble_peak_idx=peak_idx,
        h_est=H_est,
    )
