# OFDM-DQPSK Audio Transceiver

Acoustic data link using a laptop speaker and microphone as the physical channel.

**Course:** EE3005 — Communication Systems, IIT Madras  
**Authors:** Aadarsh Ramachandran (EE23B001), Manoj NH (EE23B044)

## Overview

This project implements a complete OFDM transceiver with differential QPSK (DQPSK) for indoor acoustic communication. A Zadoff–Chu preamble handles frame sync and channel estimation; two pilot subcarriers track residual carrier frequency offset (CFO).

**Live acoustic result:** ~**7.2 kbps** at ~**1.3% BER** on commodity laptop hardware.

The link is **offline / store-and-forward**, not real-time: the transmitter writes a WAV, that audio is played over the speaker while the microphone records a separate WAV, and the receiver processes the recording afterward.

Design details, equations, and analysis are in the project report: `[report.pdf](docs/report.pdf)`.

## Bit source (`TDC_Binary.csv`)

Payload bits come from a single-column CSV with **no header** — one bit (`0` or `1`) per row. The loader (`src/ofdm_dqpsk/bits.py`) flattens that column, keeps the first `10⁵` bits by default, zero-pads to a multiple of 180 bits (90 DQPSK subcarriers × 2 bits), and reshapes into OFDM symbol rows for the transmitter. The same file is passed to the receiver for BER comparison against the decoded bits.

## Repository layout

```
src/ofdm_dqpsk/     # transmitter, receiver, preamble, config
scripts/            # CLI entry points
report.pdf          # full report
```

## Quick start

```bash
pip install -e .

pip install -r requirements.txt

# 1. Build TX WAV from the bit CSV
python scripts/generate_tx.py --bits TDC_Binary.csv --out dpsk_ofdm_tx.wav

# 2a. Optional: AWGN simulation (no speaker/mic)
python scripts/simulate_channel.py --tx dpsk_ofdm_tx.wav --rx dqpsk_ofdm_rx.wav --snr-db 10

# 2b. Or play dpsk_ofdm_tx.wav on the speaker, then record the mic
python scripts/record_rx.py --out final_ofdm_rx.wav

# 3. Decode the recorded WAV and compute BER (offline)
python scripts/run_rx.py --rx final_ofdm_rx.wav --bits TDC_Binary.csv
```

## System snapshot


| Parameter   | Value              |
| ----------- | ------------------ |
| Sample rate | 48 kHz             |
| Subcarriers | 90 data + 2 pilots |
| Modulation  | DQPSK              |
| Symbol / CP | 20 ms / 5 ms       |
| Band        | ~1–19.4 kHz        |


