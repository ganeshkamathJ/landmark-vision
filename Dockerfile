# ── HuggingFace Spaces — Landmark Vision ────────────────────────
# Spaces requires port 7860 and a Dockerfile for Flask apps.
# TensorFlow is omitted (heavy ~500 MB); predictions use the
# free HuggingFace Inference API (Qwen3-VL) instead.
# ────────────────────────────────────────────────────────────────

FROM python:3.10-slim

# Install OS deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies (lightweight — no TensorFlow)
RUN pip install --no-cache-dir \
    Flask>=3.0.0 \
    Pillow>=10.0.0 \
    numpy>=1.26.0 \
    Werkzeug>=3.0.0 \
    gunicorn>=22.0.0

# Copy application code
COPY . .

# Create required directories
RUN mkdir -p uploads data

# HuggingFace Spaces requires port 7860
EXPOSE 7860

ENV PORT=7860
ENV FLASK_ENV=production

# Run with gunicorn (production WSGI server)
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:7860", "--timeout", "120", "run:app"]
