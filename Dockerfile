# Minimal terminal coding agent.
#
# Built from the published GitHub repo (approach B): the image clones
# aldenowang/SamplePythonAgent and installs it. The container doubles as a
# sandbox - the agent reads/writes files and runs shell commands in its working
# directory (/workspace), which you mount at run time.

FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Tools the agent commonly needs via the bash tool.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone and install the published agent. Override the repo/ref at build time:
#   docker build --build-arg AGENT_REF=<branch-or-tag> -t mini-coding-agent .
ARG AGENT_REPO=https://github.com/aldenowang/SamplePythonAgent.git
ARG AGENT_REF=main
RUN git clone --depth 1 --branch "$AGENT_REF" "$AGENT_REPO" SamplePythonAgent \
    && pip install -r SamplePythonAgent/requirements.txt \
    && pip install --no-deps ./SamplePythonAgent

# The agent operates on its current working directory; mount your project here.
WORKDIR /workspace

# Interactive REPL. Run with:
#   docker run -it --env-file .env -v ${PWD}/workspace:/workspace mini-coding-agent
ENTRYPOINT ["python", "-m", "cmu_project.main"]
