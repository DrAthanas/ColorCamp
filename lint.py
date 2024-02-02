import argparse
import logging
from pylint.lint import Run


logging.getLogger().setLevel(logging.INFO)

parser = argparse.ArgumentParser(prog="LINT")

parser.add_argument(
    "-p",
    "--path",
    help="path to directory you want to run pylint | "
    "Default: %(default)s | "
    "Type: %(type)s ",
    default="./src",
    type=str,
)

parser.add_argument(
    "-t",
    "--threshold",
    help="score threshold to fail pylint runner | "
    "Default: %(default)s | "
    "Type: %(type)s ",
    default=7,
    type=float,
)

args = parser.parse_args()
path = str(args.path)
threshold = float(args.threshold)

logging.info(
    "PyLint Starting | " "Path: {} | " "Threshold: {} ".format(path, threshold)
)

results = Run([path], do_exit=False)

final_score = results.linter.stats.global_note

failed = final_score < threshold

message = (
    f"PyLint {'Failed' if failed else 'Passed'} | "
    f"Score: {final_score:.2f} | "
    f"Threshold: {threshold:.1f} "
)

if failed:
    logging.error(message)
    raise Exception(message)

else:
    logging.info(message)
    exit(0)
