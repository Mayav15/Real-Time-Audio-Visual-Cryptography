# Real-Time Audio-Visual Cryptography

A real-time encryption project for video and audio streams, designed for low-latency teleconferencing where data confidentiality matters. Combines **RSA**, **Diffie-Hellman key exchange**, and **mono-alphabetic substitution** to secure A/V transmission with minimal computational overhead.

> **Note:** this is a self-contained project — *not* the artifact for any published paper. For a different, publication-backed cryptography scheme (Affine + RSA + XOR) developed during my research assistantship at DJSCE, see [DOI: 10.1007/s11042-023-16401-x](https://doi.org/10.1007/s11042-023-16401-x).

## Highlights

- **Combines three primitives**: RSA + Diffie-Hellman for key establishment, mono-alphabetic substitution for the stream cipher
- **Real-time A/V**: encrypts both video frames (OpenCV) and audio (PyAudio) end-to-end
- **C-accelerated hot paths** to keep encryption overhead inside live-stream timing budgets
- **Benchmarked against AES, RC4, and ChaCha20** on identical inputs to characterize the pipeline's performance envelope

## Architecture

```
Webcam frames + Mic audio
        │
        ▼
[ OpenCV / PyAudio capture ]
        │
        ▼
[ Encryption: RSA + DH key exchange + mono-alphabetic substitution ]
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
