# audio_plotting.py
import matplotlib.pyplot as plt
import librosa.display
import io
import base64
import numpy as np
from audio_analysis.audio_processing import calculate_spectral_features


def plot_waveform(y, sr):
    """Plot the waveform of an audio signal and return as base64 HTML."""
    fig_waveform = plt.figure(figsize=(8, 4))
    librosa.display.waveshow(y, sr=sr, alpha=0.5)
    plt.title('Waveform', fontsize=14)
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Amplitude', fontsize=12)
    plt.tight_layout()

    return fig_to_base64(fig_waveform)


def plot_spectral_features(y, sr):
    """Plot spectral features and return as base64 HTML."""
    spectral_centroids, spectral_bandwidth, spectral_rolloff, times = calculate_spectral_features(
        y, sr)

    fig_spectral_features = plt.figure(figsize=(8, 4))
    plt.semilogy(times, spectral_centroids, label='Spectral Centroid')
    plt.semilogy(times, spectral_bandwidth, label='Spectral Bandwidth')
    plt.semilogy(times, spectral_rolloff,
                 label='Spectral Rolloff', linestyle='--')
    plt.title('Spectral Features', fontsize=14)
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Hz', fontsize=12)
    plt.legend(loc='upper right')
    plt.tight_layout()

    return fig_to_base64(fig_spectral_features)


def plot_frequency_spectrum(freqs, S_mean):
    """Plot the frequency spectrum and return as base64 HTML."""
    fig_spectrum = plt.figure(figsize=(8, 4))
    plt.semilogx(freqs, 20 * np.log10(S_mean + 1e-10))  # Avoid log(0)
    plt.xlabel('Frequency (Hz)', fontsize=12)
    plt.ylabel('Amplitude (dB)', fontsize=12)
    plt.title('Frequency Spectrum', fontsize=14)
    plt.grid(True, which='both', ls='--')
    plt.xlim(20, max(freqs))
    plt.tight_layout()

    return fig_to_base64(fig_spectrum)


def plot_spectrogram(S_db, sr, hop_length):
    """Plot the spectrogram and return as base64 HTML."""
    fig_spectrogram = plt.figure(figsize=(8, 4))
    librosa.display.specshow(S_db, sr=sr, x_axis='time',
                             y_axis='linear', hop_length=hop_length)
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram', fontsize=14)
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Frequency (Hz)', fontsize=12)
    plt.tight_layout()

    return fig_to_base64(fig_spectrogram)


def plot_histogram(y):
    """Plot histogram of sample values and return as base64 HTML."""
    fig_histogram = plt.figure(figsize=(8, 4))
    plt.hist(y, bins=1000, alpha=0.7, edgecolor='black', log=True)
    plt.xlabel('Amplitude', fontsize=12)
    plt.ylabel('Count (log scale)', fontsize=12)
    plt.title('Histogram of Sample Amplitudes', fontsize=14)
    plt.grid(True)
    plt.tight_layout()

    return fig_to_base64(fig_histogram)


def fig_to_base64(fig):
    """Convert a Matplotlib figure to a base64-encoded HTML image."""
    img = io.BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight')
    plt.close(fig)
    img.seek(0)
    return f'<img src="data:image/png;base64,{base64.b64encode(img.read()).decode("utf-8")}" alt="Plot">'
