import os
from audio_analysis.audio_processing import (
    load_audio_file, get_bit_depth_info, calculate_fft_parameters,
    analyze_frequency_content, calculate_spectral_features,
    estimate_high_frequency_content, estimate_dynamic_range_and_bit_depth
)
from audio_analysis.audio_plotting import (
    plot_waveform, plot_spectral_features, plot_frequency_spectrum,
    plot_spectrogram, plot_histogram
)
from audio_analysis.utility import get_audio_files_from_folder, generate_error_message


def analyze_audio_files(files, folder_path):
    output_html = ""
    file_paths = []

    # Collect file paths
    try:
        if files:
            file_paths.extend(files)
        if folder_path:
            file_paths.extend(get_audio_files_from_folder(folder_path))
            if not file_paths:
                return f"<p><strong>Folder not found or empty:</strong> {folder_path}</p>"
    except Exception as e:
        return f"<p><strong>Error processing folder path:</strong> {str(e)}</p>"

    for audio_file in file_paths:
        try:
            # Load audio file and get bit depth
            try:
                y, sr = load_audio_file(audio_file)
                bit_depth_info = get_bit_depth_info(audio_file)
            except Exception as e:
                output_html += generate_error_message(
                    audio_file, f"Loading Error: {str(e)}")
                continue

            # Perform frequency domain analysis
            n_fft, hop_length = calculate_fft_parameters(sr)
            try:
                S, S_db, S_mean, freqs = analyze_frequency_content(
                    y, sr, n_fft, hop_length)
            except Exception as e:
                output_html += generate_error_message(
                    audio_file, f"Frequency Analysis Error: {str(e)}")
                continue

            # Generate plots
            try:
                waveform_html = plot_waveform(y, sr)
                spectral_features_html = plot_spectral_features(y, sr)
                spectrum_html = plot_frequency_spectrum(freqs, S_mean)
                spectrogram_html = plot_spectrogram(S_db, sr, hop_length)
                histogram_html = plot_histogram(y)
            except Exception as e:
                waveform_html = spectral_features_html = spectrum_html = spectrogram_html = histogram_html = generate_error_message(
                    audio_file, f"Plotting Error: {str(e)}")

            # Additional analysis
            highest_freq, estimated_sample_rate = estimate_high_frequency_content(
                S_mean, freqs)
            dynamic_range_db, estimated_bit_depth = estimate_dynamic_range_and_bit_depth(
                y)
            significant_freq_text = f"{highest_freq:.2f} Hz" if highest_freq else "No significant frequency content detected."
            estimated_sample_rate_text = f"{estimated_sample_rate / 1000:.2f} kHz" if estimated_sample_rate else "N/A"

            # Prepare the output text as an HTML table
            output_text = f"""
            <h3 style="font-size:22px;">{os.path.basename(audio_file)}</h3>
            <table style="font-size:18px;">
              <tr><td><strong>File Bit Depth:</strong></td><td>{bit_depth_info}</td></tr>
              <tr><td><strong>Sample Rate:</strong></td><td>{sr} Hz</td></tr>
              <tr><td><strong>Duration:</strong></td><td>{len(y) / sr:.2f} seconds</td></tr>
              <tr><td><strong>Using n_fft =</strong></td><td>{n_fft}</td></tr>
              <tr><td><strong>Significant frequency content up to:</strong></td><td>{significant_freq_text}</td></tr>
              <tr><td><strong>Estimated Real Sample Rate:</strong></td><td>{estimated_sample_rate_text}</td></tr>
              <tr><td><strong>Estimated Dynamic Range:</strong></td><td>{dynamic_range_db:.2f} dB</td></tr>
              <tr><td><strong>Estimated Effective Bit Depth:</strong></td><td>{estimated_bit_depth} bits PCM</td></tr>
            </table>
            """

            # Combine text and images into HTML
            output_html += f"""
            {output_text}
            <h4 style="font-size:20px;">Waveform</h4>
            {waveform_html}
            <h4 style="font-size:20px;">Spectral Features</h4>
            {spectral_features_html}
            <h4 style="font-size:20px;">Frequency Spectrum</h4>
            {spectrum_html}
            <h4 style="font-size:20px;">Spectrogram</h4>
            {spectrogram_html}
            <h4 style="font-size:20px;">Histogram of Sample Amplitudes</h4>
            {histogram_html}
            <hr>
            """
        except Exception as e:
            # Handle unexpected errors gracefully
            output_html += generate_error_message(audio_file, e)

    # Return the aggregated HTML output
    return output_html
