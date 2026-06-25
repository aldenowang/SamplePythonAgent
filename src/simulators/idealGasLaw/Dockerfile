# Standalone image for the Ideal Gas Law simulation only.
#
# Build (from inside this folder):
#   docker build -t idealgaslaw .
# Run:
#   docker run --rm idealgaslaw

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /sim

COPY idealGasLaw.py /sim/

CMD ["python", "idealGasLaw.py"]
