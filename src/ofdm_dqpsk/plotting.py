"""Receiver diagnostic plots."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .config import DEFAULT_CONFIG, SystemConfig


def plot_constellation(
    diff_symbols: np.ndarray,
    original_data: np.ndarray,
    cfg: SystemConfig = DEFAULT_CONFIG,
    save_path: str | Path | None = None,
    show: bool = True,
) -> None:
    num_data_syms = diff_symbols.shape[0]
    pts = diff_symbols.flatten()
    tx_bits_ref = original_data[:num_data_syms]

    true_labels = np.zeros((num_data_syms, cfg.num_data_bins), dtype=int)
    for sym in range(num_data_syms):
        for sc in range(cfg.num_data_bins):
            b0 = int(tx_bits_ref[sym, sc * 2])
            b1 = int(tx_bits_ref[sym, sc * 2 + 1])
            true_labels[sym, sc] = cfg.dibit_to_idx[(b0, b1)]

    labels = true_labels.flatten()
    colors = ["tab:blue", "tab:orange", "tab:green", "tab:red"]

    plt.figure(figsize=(7, 7))
    for k in range(4):
        mask = labels == k
        plt.scatter(
            pts[mask].real,
            pts[mask].imag,
            s=8,
            alpha=0.45,
            color=colors[k],
        )

    plt.xlabel("In-Phase (Re)")
    plt.ylabel("Quadrature (Im)")
    # Matches notebook axis limits used for the live-recording constellation.
    plt.xlim(-1e-8, 1e-8)
    plt.ylim(-1e-8, 1e-8)
    plt.title("DQPSK Differential Constellation")

    if save_path is not None:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()


def plot_phase_histogram(
    diff_symbols: np.ndarray,
    save_path: str | Path | None = None,
    show: bool = True,
) -> None:
    angles = np.angle(diff_symbols.flatten()) % (2 * np.pi)

    plt.figure(figsize=(8, 4))
    plt.hist(angles, bins=200)
    for p in [0, np.pi / 2, np.pi, 3 * np.pi / 2]:
        plt.axvline(p)

    plt.xticks(
        [0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi],
        ["0", "π/2", "π", "3π/2", "2π"],
    )
    plt.title("DQPSK Differential Phase Distribution")
    plt.xlabel("Phase")
    plt.ylabel("Count")
    plt.grid(True)

    if save_path is not None:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()
