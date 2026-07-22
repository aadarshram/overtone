#!/usr/bin/env python3
"""Optional AWGN + delay channel simulation (notebook helper)."""

from __future__ import annotations

import argparse
from pathlib import Path

import _bootstrap  # noqa: F401

from ofdm_dqpsk.channel import simulate_channel


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tx", type=Path, default=Path("dpsk_ofdm_tx.wav"))
    parser.add_argument("--rx", type=Path, default=Path("dqpsk_ofdm_rx.wav"))
    parser.add_argument("--snr-db", type=float, default=10.0)
    parser.add_argument("--delay-sec", type=float, default=0.0)
    args = parser.parse_args()

    simulate_channel(
        args.tx,
        args.rx,
        snr_db=args.snr_db,
        delay_sec=args.delay_sec,
    )


if __name__ == "__main__":
    main()
