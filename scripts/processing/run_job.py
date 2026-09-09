"""Run one preview job from the command line."""

import argparse
import json

from workers.processing_worker import run_once


def main():
    parser = argparse.ArgumentParser(description="Process one coursework resource")
    parser.add_argument("resource_file_id")
    parser.add_argument("input_path")
    parser.add_argument("output_dir")
    parser.add_argument("jobs_path")
    arguments = parser.parse_args()
    job = run_once(
        arguments.resource_file_id,
        arguments.input_path,
        arguments.output_dir,
        arguments.jobs_path,
    )
    print(json.dumps(job.as_dict(), sort_keys=True))


if __name__ == "__main__":
    main()