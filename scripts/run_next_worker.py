"""Run the autonomous job worker locally."""

from clearcouncil_next.jobs.runner import run_worker_forever


if __name__ == "__main__":
    run_worker_forever()
