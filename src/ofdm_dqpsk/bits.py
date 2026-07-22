"""Bit loading and framing helpers."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .config import DEFAULT_CONFIG, SystemConfig


def load_bit_matrix(
    csv_path: str | Path,
    cfg: SystemConfig = DEFAULT_CONFIG,
    num_bits: int | None = None,
) -> np.ndarray:
    """Load bits from CSV, truncate, pad, and reshape to (num_symbols, num_bit_cols)."""
    n_bits = cfg.num_bits if num_bits is None else num_bits

    tx_bits = (
        pd.read_csv(csv_path, header=None).values.flatten().astype(np.uint8)
    )
    tx_bits = tx_bits[:n_bits]

    pad = (-len(tx_bits)) % cfg.num_bit_cols
    if pad > 0:
        tx_bits = np.concatenate([tx_bits, np.zeros(pad, dtype=np.uint8)])

    return tx_bits.reshape(-1, cfg.num_bit_cols)
