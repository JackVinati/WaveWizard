import librosa
import soundfile as sf
import numpy as np
import os


def load_audio_file(audio_file):
    """Load an audio file and return the audio time series and sampling rate."""
    y, sr = librosa.load(audio_file, sr=None)
    return y, sr


def get_bit_depth_info(audio_file):
    """Get the original bit depth from file metadata."""
    with sf.SoundFile(audio_file) as f:
        return f.subtype_info


def calculate_fft_parameters(sr, desired_freq_resolution=10.0):
    """Calculate FFT parameters such as n_fft and hop_length."""
    n_fft = int(sr / desired_freq_resolution)
    n_fft = 2 ** int(np.ceil(np.log2(n_fft)))  # Next power of two
    max_n_fft = 32768
    min_n_fft = 1024
    n_fft = min(max(n_fft, min_n_fft), max_n_fft)
    hop_length = n_fft // 4
    return n_fft, hop_length


def analyze_frequency_content(y, sr, n_fft, hop_length):
    """Compute the Short-Time Fourier Transform and frequency content."""
    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
    S_db = librosa.amplitude_to_db(S, ref=np.max)
    S_mean = np.mean(S, axis=1)
    freqs = np.linspace(0, sr / 2, len(S_mean))
    return S, S_db, S_mean, freqs


def estimate_high_frequency_content(S_mean, freqs, threshold_db=-80):
    """Estimate the highest frequency with significant content."""
    max_amplitude_db = 20 * np.log10(np.max(S_mean + 1e-10))
    threshold_amplitude_db = max_amplitude_db + threshold_db
    threshold_amplitude = 10 ** (threshold_amplitude_db / 20)

    significant_indices = np.where(S_mean >= threshold_amplitude)[0]
    if len(significant_indices) > 0:
        highest_freq = freqs[significant_indices[-1]]
        estimated_sample_rate = highest_freq * 2  # Nyquist theorem
        return highest_freq, estimated_sample_rate
    return None, None


def calculate_spectral_features(y, sr):
    """Calculate spectral features: spectral centroid, spectral bandwidth, and spectral rolloff."""
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
    spectral_rolloff = librosa.feature.spectral_rolloff(
        y=y, sr=sr, roll_percent=0.85)[0]
    times = librosa.times_like(spectral_centroids)
    return spectral_centroids, spectral_bandwidth, spectral_rolloff, times


def estimate_dynamic_range_and_bit_depth(y):
    """Estimate effective bit depth and dynamic range."""
    signal_rms = np.sqrt(np.mean(y ** 2))
    noise_floor = np.percentile(np.abs(y), 0.1)
    dynamic_range_db = 20 * np.log10(signal_rms / (noise_floor + 1e-10))
    estimated_bit_depth = int(np.ceil(dynamic_range_db / 6.02))
    return dynamic_range_db, estimated_bit_depth
