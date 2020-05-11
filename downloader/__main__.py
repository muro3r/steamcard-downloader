import argparse
import logging

from .downloader import main

parser = argparse.ArgumentParser(prog="Steamcard Downloader")
parser.add_argument("appId", nargs="+", type=int)

args = parser.parse_args()

for appId in args.appId:
    main(appId)

logging.info("Process complete!")
