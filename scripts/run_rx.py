#!/usr/bin/env python3
"""Run the OFDM-DQPSK receiver on a recorded (or simulated) WAV."""

from __future__ import annotations

import argparse
from pathlib import Path

import _bootstrap  # noqa: F401

from ofdm_dqpsk.bits import load_bit_matrix
from ofdm_dqpsk.config import DEFAULT_CONFIG
from ofdm_dqpsk.receiver import run_receiver


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rx",
        type=Path,
        default=Path("final_ofdm_rx.wav"),
        help="Received WAV path",
    )
    parser.add_argument(
        "--bits",
        type=Path,
        default=Path("TDC_Binary.csv"),
        help="Original TX bit CSV (for BER)",
    )
    parser.add_argument(
        "--num-bits",
        type=int,
        default=DEFAULT_CONFIG.num_bits,
    )
    parser.add_argument(
        "--rx-bits-out",
        type=Path,
        default=Path("rx_bits.csv"),
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Skip matplotlib display",
    )
    parser.add_argument(
        "--save-constellation",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--save-histogram",
        type=Path,
        default=None,
    )
    args = parser.parse_args()

    original_data = load_bit_matrix(args.bits, num_bits=args.num_bits)
    run_receiver(
        args.rx,
        original_data,
        plot=not args.no_plot,
        save_rx_bits=args.rx_bits_out,
        constellation_path=args.save_constellation,
        histogram_path=args.save_histogram,
    )


if __name__ == "__main__":
    main()
