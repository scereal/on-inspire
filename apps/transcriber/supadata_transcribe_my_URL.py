import os
import subprocess
import sys

from supadata import Supadata, SupadataError

# The API key comes from an environment variable so it never ends up in the (public) repo.
# Set it once in ~/.zshrc:  export SUPADATA_API_KEY="sd_..."
api_key = os.environ.get("SUPADATA_API_KEY")
if not api_key:
    sys.exit('SUPADATA_API_KEY is not set. Add  export SUPADATA_API_KEY="sd_..."  to ~/.zshrc, then open a new terminal.')

# Take the URL from the command line, or ask for it
url = sys.argv[1] if len(sys.argv) > 1 else input("Paste a video URL: ").strip()
if not url.startswith(("http://", "https://")):
    sys.exit(f"That doesn't look like a URL: {url!r}")

# Initialize the client
supadata = Supadata(api_key=api_key)

# Get transcript from any supported platform (YouTube, TikTok, Instagram, X (Twitter), Facebook, file URLs)
try:
    transcript = supadata.transcript(
        url=url,
        lang="en",  # Optional: preferred language
        text=True,  # Optional: return plain text instead of timestamped chunks
        mode="auto"  # Optional: "native", "auto", or "generate"
    )
except SupadataError as e:
    sys.exit(f"Supadata couldn't transcribe that URL: {e}")

content = None

# For immediate results
if hasattr(transcript, 'content'):
    content = transcript.content
    print(f"Transcript: {content}")
    print(f"Language: {transcript.lang}")
else:
    # For async processing (large files)
    print(f"Processing started with job ID: {transcript.job_id}")
    # Poll for results (requires supadata >= 1.7.0)
    job = supadata.transcript.get_job_status(transcript.job_id)
    if job.status == "completed":
        content = job.result.content
        print(f"Transcript: {content}")
    elif job.status == "failed":
        print(f"Transcript failed: {job.error}")
    else:
        print(f"Job status: {job.status}")  # 'queued' or 'active'

# Copy the transcript to the clipboard (macOS)
if content:
    subprocess.run("pbcopy", input=content, text=True, check=True)
    print("Transcript copied to clipboard.")
