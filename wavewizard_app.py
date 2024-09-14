import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import soundfile as sf
import gradio as gr
import io
import os
import base64


def analyze_audio_files(files, folder_path):
    output_html = ""
    file_paths = []

    # Handle inputs: files can be a list of file paths or a folder path
    if files:
        file_paths.extend(files)
    if folder_path:
        if os.path.isdir(folder_path):
            folder_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                            if os.path.isfile(os.path.join(folder_path, f))]
            file_paths.extend(folder_files)
        else:
            return f"<p><strong>Folder not found:</strong> {folder_path}</p>"

    for audio_file in file_paths:
        try:
            # Load the audio file
            y, sr = librosa.load(audio_file, sr=None)

            # Get original bit depth from file metadata
            with sf.SoundFile(audio_file) as f:
                bit_depth_info = f.subtype_info

            # Time domain analysis
            duration = len(y) / sr

            # Frequency domain analysis
            desired_freq_resolution = 10.0  # in Hz

            # Calculate n_fft, limit it to a reasonable range
            n_fft = int(sr / desired_freq_resolution)
            n_fft = 2 ** int(np.ceil(np.log2(n_fft)))  # Next power of two

            # Set maximum and minimum n_fft to avoid excessive computation
            max_n_fft = 32768
            min_n_fft = 1024
            n_fft = min(max(n_fft, min_n_fft), max_n_fft)

            hop_length = n_fft // 4

            # Compute the Short-Time Fourier Transform (STFT)
            S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))

            # Compute the spectrogram (in dB)
            S_db = librosa.amplitude_to_db(S, ref=np.max)

            # Average over time to get the frequency spectrum
            S_mean = np.mean(S, axis=1)
            freqs = np.linspace(0, sr / 2, len(S_mean))

            # Plot the frequency spectrum
            fig1 = plt.figure(figsize=(8, 4))
            plt.semilogx(freqs, 20 * np.log10(S_mean + 1e-10))  # Avoid log(0)
            plt.xlabel('Frequency (Hz)', fontsize=12)
            plt.ylabel('Amplitude (dB)', fontsize=12)
            plt.title('Frequency Spectrum', fontsize=14)
            plt.grid(True, which='both', ls='--')
            plt.xlim(20, sr / 2)
            plt.tight_layout()
            spectrum_image = io.BytesIO()
            plt.savefig(spectrum_image, format='png', bbox_inches='tight')
            plt.close(fig1)
            spectrum_image.seek(0)
            spectrum_base64 = base64.b64encode(
                spectrum_image.read()).decode('utf-8')
            spectrum_html = f'<img src="data:image/png;base64,{spectrum_base64}" alt="Frequency Spectrum">'

            # Plot the spectrogram
            fig3 = plt.figure(figsize=(8, 4))
            librosa.display.specshow(
                S_db, sr=sr, x_axis='time', y_axis='linear', hop_length=hop_length)
            plt.colorbar(format='%+2.0f dB')
            plt.title('Spectrogram', fontsize=14)
            plt.xlabel('Time (s)', fontsize=12)
            plt.ylabel('Frequency (Hz)', fontsize=12)
            plt.tight_layout()
            spectrogram_image = io.BytesIO()
            plt.savefig(spectrogram_image, format='png', bbox_inches='tight')
            plt.close(fig3)
            spectrogram_image.seek(0)
            spectrogram_base64 = base64.b64encode(
                spectrogram_image.read()).decode('utf-8')
            spectrogram_html = f'<img src="data:image/png;base64,{spectrogram_base64}" alt="Spectrogram">'

            # Analyze high-frequency content
            # Define a threshold relative to the maximum amplitude
            threshold_db = -80  # dB
            max_amplitude_db = 20 * np.log10(np.max(S_mean + 1e-10))
            threshold_amplitude_db = max_amplitude_db + threshold_db
            threshold_amplitude = 10 ** (threshold_amplitude_db / 20)

            # Find the highest frequency with significant content
            significant_indices = np.where(S_mean >= threshold_amplitude)[0]
            if len(significant_indices) > 0:
                highest_freq = freqs[significant_indices[-1]]

                # Estimate the real sample rate
                estimated_sample_rate = highest_freq * 2  # Nyquist theorem

                significant_freq_text = f"{highest_freq:.2f} Hz"
                estimated_sample_rate_text = f"{estimated_sample_rate / 1000:.2f} kHz"
            else:
                significant_freq_text = "No significant frequency content detected."
                estimated_sample_rate_text = "N/A"

            # Estimate effective bit depth
            # Calculate the signal's dynamic range
            signal_rms = np.sqrt(np.mean(y ** 2))
            noise_floor = np.percentile(np.abs(y), 0.1)
            # Avoid division by zero
            dynamic_range_db = 20 * \
                np.log10(signal_rms / (noise_floor + 1e-10))

            estimated_bit_depth = int(np.ceil(dynamic_range_db / 6.02))

            # Prepare the output text as an HTML table
            output_text = f"""
            <h3 style="font-size:22px;">{os.path.basename(audio_file)}</h3>
            <table style="font-size:18px;">
              <tr><td><strong>File Bit Depth:</strong></td><td>{bit_depth_info}</td></tr>
              <tr><td><strong>Sample Rate:</strong></td><td>{sr} Hz</td></tr>
              <tr><td><strong>Duration:</strong></td><td>{duration:.2f} seconds</td></tr>
              <tr><td><strong>Using n_fft =</strong></td><td>{n_fft}</td></tr>
              <tr><td><strong>Significant frequency content up to:</strong></td><td>{significant_freq_text}</td></tr>
              <tr><td><strong>Estimated Real Sample Rate:</strong></td><td>{estimated_sample_rate_text}</td></tr>
              <tr><td><strong>Estimated Dynamic Range:</strong></td><td>{dynamic_range_db:.2f} dB</td></tr>
              <tr><td><strong>Estimated Effective Bit Depth:</strong></td><td>{estimated_bit_depth} bits PCM</td></tr>
            </table>
            """

            # Plot histogram of sample values
            fig2 = plt.figure(figsize=(8, 4))
            plt.hist(y, bins=1000, alpha=0.7, color='blue',
                     edgecolor='black', log=True)
            plt.xlabel('Amplitude', fontsize=12)
            plt.ylabel('Count (log scale)', fontsize=12)
            plt.title('Histogram of Sample Amplitudes', fontsize=14)
            plt.grid(True)
            plt.tight_layout()
            histogram_image = io.BytesIO()
            plt.savefig(histogram_image, format='png', bbox_inches='tight')
            plt.close(fig2)
            histogram_image.seek(0)
            histogram_base64 = base64.b64encode(
                histogram_image.read()).decode('utf-8')
            histogram_html = f'<img src="data:image/png;base64,{histogram_base64}" alt="Histogram of Sample Amplitudes">'

            # Combine text and images into HTML
            output_html += f"""
            {output_text}
            <h4 style="font-size:20px;">Frequency Spectrum</h4>
            {spectrum_html}
            <h4 style="font-size:20px;">Spectrogram</h4>
            {spectrogram_html}
            <h4 style="font-size:20px;">Histogram of Sample Amplitudes</h4>
            {histogram_html}
            <hr>
            """
        except Exception as e:
            # Handle errors gracefully
            output_html += f"<p><strong>File:</strong> {os.path.basename(audio_file)}</p><p><strong>Error:</strong> {str(e)}</p><hr>"

    # Return the aggregated HTML output
    return output_html


with gr.Blocks() as demo:
    gr.Markdown("Wave Wizard")
    gr.Markdown(
        "Upload one or more audio files, or specify a folder containing audio files.")
    with gr.Row():
        file_input = gr.Files(label="Upload Audio Files",
                              type="filepath", file_count="multiple")
        folder_input = gr.Textbox(label="Folder Path (optional)",
                                  placeholder="Enter folder path containing audio files")
    analyze_button = gr.Button("Analyze")
    output_display = gr.HTML()

    def analyze_wrapper(files, folder_path):
        outputs = analyze_audio_files(files, folder_path)
        return outputs

    analyze_button.click(analyze_wrapper, inputs=[
                         file_input, folder_input], outputs=output_display)

demo.launch()
