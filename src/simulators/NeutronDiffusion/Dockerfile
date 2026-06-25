# Standalone image for the 1D Neutron Diffusion simulation only.
#
# Build (from inside this folder):
#   docker build -t 1dneutrondiffusion .
# Run:
#   docker run --rm 1dneutrondiffusion

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /sim

COPY 1DNeutronDiffusion.py /sim/

CMD ["python", "1DNeutronDiffusion.py"]
