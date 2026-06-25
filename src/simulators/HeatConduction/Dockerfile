# Standalone image for the 1D Heat Conduction simulation only.
#
# Build (from inside this folder):
#   docker build -t 1dheatconduction .
# Run:
#   docker run --rm 1dheatconduction

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /sim

COPY 1DHeatConduction.py /sim/

CMD ["python", "1DHeatConduction.py"]
