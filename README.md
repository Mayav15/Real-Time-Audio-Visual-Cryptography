# Real-Time Audio-Visual Cryptography

A real-time encryption pipeline for video and audio streams, designed for low-latency teleconferencing where data confidentiality matters. Combines **RSA**, **Diffie-Hellman key exchange**, and **mono-alphabetic substitution** to secure A/V transmission against differential, statistical, and brute-force attacks.


## Highlights

- **Hybrid scheme**: Affine Cipher + RSA + XOR — hardens against multiple attack classes simultaneously
- **Real-time benchmarks**: 174.25 ns/pixel encryption, 136.38 ns/pixel decryption — well inside live-stream timing budgets
- **Beats common alternatives** on encryption/decryption time: compared head-to-head against AES, RC4, and ChaCha20 on identical inputs

## Architecture

```
Webcam frames + Mic audio
        │
        ▼
[ OpenCV / PyAudio capture ]
        │
        ▼
[ Hybrid encryption: Affine + RSA + XOR ]
        │
        ▼
[ Encrypted stream over network ]
        │
        ▼
[ Decryption + playback ]
```

## Tech Stack

- **Python** for the orchestration layer (OpenCV, PyAudio)
- **C** for performance-critical encryption hot paths
- OpenCV for video capture
- PyAudio for audio capture

## Repository structure

- [`Implementation/`](./Implementation/) — main source
- [`Evaluation and Comparison/`](./Evaluation%20and%20Comparison/) — benchmark scripts and result data
- [`Enhancing Security in Real-Time Audio and Video Communication.PDF`](./Enhancing%20Security%20in%20Real-Time%20Audio%20and%20Video%20Communication.PDF) — supplementary writeup


