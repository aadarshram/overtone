"""System parameters for the OFDM-DQPSK audio transceiver."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass(frozen=True)
class SystemConfig:
    num_data_bins: int = 90
    bits_per_symbol: int = 2  # DQPSK
    fs: int = 48_000
    t_sym: float = 0.02  # 20 ms per symbol
    cp_duration: float = 0.005  # 5 ms cyclic prefix
    start_freq: float = 1000.0
    spacing: float = 200.0
    zc_length: int = 61
    zc_root: int = 1
    tx_tukey_alpha: float = 0.05
    rx_tukey_alpha: float = 0.1
    silence_sec: float = 1.0
    num_bits: int = 100_000

    # Gray-coded DQPSK: (b0, b1) -> delta phase
    qpsk_phase_map: dict[tuple[int, int], float] = field(
        default_factory=lambda: {
            (0, 0): 0.0,
            (0, 1): np.pi / 2,
            (1, 1): np.pi,
            (1, 0): 3 * np.pi / 2,
        }
    )

    @property
    def pilot_indices(self) -> list[int]:
        return [0, self.num_data_bins + 1]

    @property
    def data_indices(self) -> list[int]:
        return list(range(1, self.num_data_bins + 1))

    @property
    def num_bit_cols(self) -> int:
        return self.num_data_bins * self.bits_per_symbol

    @property
    def qpsk_phase_inv(self) -> dict[float, tuple[int, int]]:
        return {v: k for k, v in self.qpsk_phase_map.items()}

    @property
    def n_samples(self) -> int:
        return int(self.fs * self.t_sym)

    @property
    def cp_samples(self) -> int:
        return int(self.fs * self.cp_duration)

    @property
    def total_sym_samples(self) -> int:
        return self.n_samples + self.cp_samples

    @property
    def bin_spacing(self) -> int:
        return int(self.spacing / (self.fs / self.n_samples))

    @property
    def start_bin(self) -> int:
        return int(self.start_freq / (self.fs / self.n_samples))

    @property
    def idx_to_dibit(self) -> dict[int, tuple[int, int]]:
        return {
            0: (0, 0),
            1: (0, 1),
            2: (1, 1),
            3: (1, 0),
        }

    @property
    def dibit_to_idx(self) -> dict[tuple[int, int], int]:
        return {v: k for k, v in self.idx_to_dibit.items()}


DEFAULT_CONFIG = SystemConfig()
