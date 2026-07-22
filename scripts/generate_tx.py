#!/usr/bin/env python3
"""Generate the OFDM-DQPSK transmit WAV from a bit CSV."""

from __future__ import annotations

import argparse
from pathlib import Path

import _bootstrap  # noqa: F401

from ofdm_dqpsk.bits import load_bit_matrix
from ofdm_dqpsk.config import DEFAULT_CONFIG
from ofdm_dqpsk.transmitter import generate_transmitter


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bits",
        type=Path,
        default=Path("TDC_Binary.csv"),
        help="CSV of binary bits (one column, no header)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("dpsk_ofdm_tx.wav"),
        help="Output TX WAV path",
    )
    parser.add_argument(
        "--num-bits",
        type=int,
        default=DEFAULT_CONFIG.num_bits,
        help="Number of information bits to load",
    )
    args = parser.parse_args()

    original_data = load_bit_matrix(args.bits, num_bits=args.num_bits)
    print("Loaded bits matrix shape:", original_data.shape)
    generate_transmitter(original_data, filename=args.out)


if __name__ == "__main__":
    main()
