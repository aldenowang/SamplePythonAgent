# Standalone image for the Radioactive Decay simulation only.
#
# Build (from inside this folder):
#   docker build -t radioactivedecay .
# Run:
#   docker run --rm radioactivedecay

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /sim

COPY RadioactiveDecay.py /sim/

CMD ["python", "RadioactiveDecay.py"]
