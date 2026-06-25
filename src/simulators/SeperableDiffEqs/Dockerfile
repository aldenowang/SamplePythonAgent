# Standalone image for the Separable Differential Equations simulation only.
#
# Build (from inside this folder):
#   docker build -t seperablediffeqs .
# Run:
#   docker run --rm seperablediffeqs

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /sim

COPY SeperableDiffEqs.py /sim/

CMD ["python", "SeperableDiffEqs.py"]
