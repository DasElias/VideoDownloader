import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import re

# Simple YouTube downloader GUI using yt-dlp
# Requirements: Python 3.x, yt-dlp installed and in PATH

# Regex to match YouTube URLs
YOUTUBE_REGEX = re.compile(r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)")

def append_status(msg):
    """Append a message to the status output box."""
    status.config(state=tk.NORMAL)
    status.insert(tk.END, msg + "\n")
    status.see(tk.END)
    status.config(state=tk.DISABLED)


def clear_status():
    """Clear the status output box."""
    status.config(state=tk.NORMAL)
    status.delete("1.0", tk.END)
    status.config(state=tk.DISABLED)


def download_videos():
    """Download each YouTube URL from the text widget, reporting status."""
    urls = text.get("1.0", tk.END).splitlines()
    if not any(urls):
        messagebox.showinfo("Info", "No URLs to download.")
        return
    append_status("Starting downloads...")
    for url in urls:
        url = url.strip()
        if not url:
            continue
        if not YOUTUBE_REGEX.search(url):
            append_status(f"Skipping invalid URL: {url}")
            continue
        append_status(f"Downloading: {url}")
        try:
            result = subprocess.run(
                ['youtube-dl', '--no-mtime', '--embed-metadata', '--embed-thubmnail', '--extract-audio', '--audio-format', 'mp3', url],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            output = result.stdout.strip()
            append_status(f"System output for {url}:\n{output}")
            if result.returncode == 0:
                append_status(f"Finished downloading: {url}")
            else:
                append_status(f"Error downloading {url}, return code {result.returncode}")
        except Exception as e:
            append_status(f"Unexpected error: {e}")
    append_status("All done.")


def on_download_click():
    """Disable the button and start download in a new thread after clearing status."""
    clear_status()
    button_download.config(state=tk.DISABLED)
    threading.Thread(target=lambda: [download_videos(), button_download.config(state=tk.NORMAL)]).start()

# Set up main window
root = tk.Tk()
root.title("YouTube Downloader")

# Configure root to allow resizing in both directions
root.rowconfigure(0, weight=1)
root.rowconfigure(3, weight=1)
root.columnconfigure(0, weight=1)

# Multi-line text field for URLs
text = tk.Text(root, width=60, height=10, bg='white', fg='black')
text.grid(row=0, column=0, padx=10, pady=(10,5), sticky='nsew')

# On launch, check clipboard and insert if it's a YouTube URL
root.update()
try:
    clip = root.clipboard_get()
    if YOUTUBE_REGEX.search(clip):
        text.insert(tk.END, clip + '\n')
except tk.TclError:
    pass

# Download button
button_download = tk.Button(root, text="Download", command=on_download_click)
button_download.grid(row=1, column=0, pady=(0,5))

# Status output
label_status = tk.Label(root, text="Status:")
label_status.grid(row=2, column=0, sticky='w', padx=10)
status = tk.Text(root, width=60, height=10, bg='white', fg='black', state=tk.DISABLED)
status.grid(row=3, column=0, padx=10, pady=(0,10), sticky='nsew')

# Start GUI event loop
root.mainloop()
