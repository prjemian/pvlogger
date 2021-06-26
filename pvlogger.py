#!/usr/bin/env python

"""
pvlogger: record EPICS PVs in text files

Motivated by an experiment at the APS.

**Objectives**

* Log a list of PVs that update asynchronous to sample measurements.
* List should be a text file that is easy to read and load.
* text file should not be too long so make a new file for each day

**HELP**

Request command-line help: ``pvlogger.py --help``
"""

from ophyd import EpicsSignalRO
import argparse
import datetime
import logging
import os
import pathlib
import threading
import time


DEFAULT_RECORDING_PERIOD_S = 10
DEFAULT_RECORDING_DURATION_S = 60 * 60
HOME_PATH = str(pathlib.Path.home())
# NOTE: assumes ~/Documents exists and is writeable!
DEFAULT_PATH = os.path.join(HOME_PATH, "Documents", "pvlogger")

logging.basicConfig(
    level=logging.WARNING,
    # level=logging.INFO,
    # level=logging.DEBUG,
    format="[%(levelname)s %(asctime)s.%(msecs)01d %(lineno)d] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class PvLogger:
    """
    Record raw values in data files.

    EXAMPLE::

        import pvlogger
        import time

        file_path = ""/tmp/pvlogger"
        pvlist = '''
            rpib4b1:temperature
            rpib4b1:humidity
            gp:UPTIME
            gp:datetime
        '''.split()
        datalogger = pvlogger.PvLogger(pvlist, path=file_path)
        datalogger.start_recording()
        time.sleep(3600)  # log data for one hour at 10s (default) intervals
        datalogger.stop_recording()

    PARAMETERS

    pvlist
        *[str]* :
        list of EPICS PV name(s) to be logged
    path
        *str* :
        Base directory path under which to store data files.
        (default: ``~/Documents/pvlogger``)
    """

    def __init__(self, pvlist, path=None):
        """Constructor."""
        logger.info("PvLogger starting")
        self.pvs = {}
        for i, pv in enumerate(pvlist):
            logger.debug("Connecting PV %s", pv)
            self.pvs[f"pv{i+1}"] = EpicsSignalRO(pv, name=f"{pv}{i+1}")
        self.base_path = path or DEFAULT_PATH
        self.file_extension = "txt"
        self.recording = None
        self.recording_period = None
        self._request_stop_recording = False
        self.recording_poll_delay = 0.1  # seconds
        logger.info("directory: %s", self.base_path)

    def get_daily_file(self, when=None):
        """
        Return absolute path to daily file.

        PARAMETERS

        when
            *obj* :
            Path will be based on this instance of `datetime.datetime`.
            (default: now)
        """
        dt = when or datetime.datetime.now()
        path = os.path.join(
            self.base_path,
            f"{dt.year:04d}",
            f"{dt.month:02d}",
            (
                f"{dt.year:04d}"
                f"-{dt.month:02d}"
                f"-{dt.day:02d}"
                f".{self.file_extension}"
            ),
        )
        return path

    def create_file(self, fname):
        """
        Create the data file (and path as necessary)

        PARAMETERS

        fname
            *str* :
            File to be created.  Absolute path.
        """
        path = os.path.split(fname)[0]

        # create path as needed
        os.makedirs(path, exist_ok=True)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Could not create directory path: {path}")

        # create file
        logger.debug("Creating log file %s", fname)
        with open(fname, "w") as f:
            created = datetime.datetime.now().isoformat(sep=" ")
            header = (
                f"# file: {fname}\n"
                f"# created: {created}\n"
                "# program: pvlogger\n"
                "# column separator: tab (^T or \\t)\n"
                "#\n"
                "# time: (UTC) seconds (since 1970-01-01T00:00:00 UTC)\n"
            )
            header += "# \n"
            header += "# time\t"
            header += "\t".join([pv.pvname for pv in self.pvs.values()])
            header += "\tymd hms\n"
            f.write(header)

    def record(self, when=None):
        """
        Record new PV values.  Create new file and path as needed.

        PARAMETERS

        when
            *obj* :
            `datetime.datetime` of these values.
            (default: now)
        """
        dt = when or datetime.datetime.now()
        fname = self.get_daily_file(dt)
        try:
            if not os.path.exists(fname):
                self.create_file(fname)
            with open(fname, "a") as f:
                record = [
                    f"{dt.timestamp():.02f}",
                ]
                for pv in self.pvs.values():
                    record.append(f"{pv.get()}")
                record.append(f"{dt}")
                values = "\t".join(record)
                f.write(values + "\n")
                logger.debug(values)
        except Exception as exc:
            logger.info("Continuing after exception: %s", exc)

    def start_recording(self, period=10):
        """
        Initiate periodic recording (or change period).

        PARAMETERS

        period
            *number* :
            interval (seconds) between recorded measurements.
            Minimum interval is 0.5 seconds.  Default is 10 seconds.
        """
        if period is None:
            period = 10
        period = max(period, 0.5)
        if self.recording_period != period:
            logger.info(
                "changing recording period from %s to %s (s)",
                self.recording_period,
                period,
            )
            self.recording_period = period

        def worker():
            """Background thread that orders recording."""
            logger.info("Periodic recording thread starting...")
            # wait for all PVs to connect
            for pv in self.pvs.values():
                if not pv.connected:
                    logger.debug("Waiting for %s to connect", pv.pvname)
                    pv.wait_for_connection()
            logger.debug("All %s PVs connected", len(self.pvs))
            next_recording = time.time()
            while not self._request_stop_recording:
                if time.time() >= next_recording:
                    next_recording += self.recording_period
                    self.record()
                time.sleep(self.recording_poll_delay)
            self._request_stop_recording = False
            self.recording = None
            logger.info("Periodic recording thread exiting...")

        self._request_stop_recording = False
        self.recording = threading.Thread(target=worker, daemon=True)
        self.recording.start()

    def stop_recording(self):
        if self.recording is not None:
            self._request_stop_recording = True


def get_inputs():
    """
    get configuration from command-line options
    """
    doc = __doc__.strip().splitlines()[0]
    parser = argparse.ArgumentParser(prog="pvlogger.py", description=doc)

    parser.add_argument(
        "pvnames", action="store", nargs="+", help="one or more EPICS PV names"
    )

    parser.add_argument(
        "--path",
        dest="path",
        action="store",
        default=DEFAULT_PATH,
        help=f"logging directory, default: {DEFAULT_PATH}",
    )

    parser.add_argument(
        "--period",
        dest="period",
        action="store",
        default=DEFAULT_RECORDING_PERIOD_S,
        help=f"recording period, default: {DEFAULT_RECORDING_PERIOD_S} (s)",
    )

    parser.add_argument(
        "--duration",
        dest="duration",
        action="store",
        default=DEFAULT_RECORDING_PERIOD_S,
        help=(
            "recording ends after this duration"
            f", default: {DEFAULT_RECORDING_DURATION_S} (s)"
        ),
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help=("logging verbosity" " (default=quiet, v=some,  vv=all)"),
    )

    return parser.parse_args()


def main():
    """
    command-line interface
    """
    args = get_inputs()
    if args.verbose == 0:
        level = logging.WARNING
    elif args.verbose == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG
    logger.setLevel(level)

    datalogger = PvLogger(args.pvnames, path=args.path)
    datalogger.start_recording(period=int(args.period))
    logger.info(
        "recording for %s s at %s s intervals", args.duration, args.period
    )
    time.sleep(int(args.duration))
    datalogger.stop_recording()


if __name__ == "__main__":
    main()
