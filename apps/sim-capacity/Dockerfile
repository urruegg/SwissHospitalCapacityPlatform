FROM python:3.11-slim

WORKDIR /repo

# Preserve the repo directory layout so calibration modules can resolve
# _REPO_ROOT via Path(__file__).parents[4]. See
# apps/sim-capacity/src/calibration/*.py.
COPY apps/sim-capacity/pyproject.toml /repo/apps/sim-capacity/
COPY apps/sim-capacity/src/ /repo/apps/sim-capacity/src/
COPY data/master-data/capacity/*.csv /repo/data/master-data/capacity/

RUN pip install --no-cache-dir /repo/apps/sim-capacity

ENV PYTHONPATH=/repo/apps/sim-capacity/src

# Continuous streaming producer. --duration-hours 0 loops forever; --rate 30 = 30 wall-clock
# seconds per simulated hour (120x accel). Runs until Container App restart or SIGTERM.
CMD ["python", "/repo/apps/sim-capacity/src/producer_sim.py", "--duration-hours", "0", "--rate", "30"]
