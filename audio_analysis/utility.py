import os


def get_audio_files_from_folder(folder_path):
    """Get a list of audio files in a folder."""
    if os.path.isdir(folder_path):
        return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    return []


def generate_error_message(audio_file, error):
    """Generate an error message for HTML output."""
    return f"<p><strong>File:</strong> {os.path.basename(audio_file)}</p><p><strong>Error:</strong> {str(error)}</p><hr>"
