# pvlogger

pvlogger: record EPICS PVs in text files

Motivated by an experiment at the APS.

**Contents**

- [pvlogger](#pvlogger)
  - [Objectives](#objectives)
  - [Required packages](#required-packages)
  - [Notes](#notes)
  - [Command-line help](#command-line-help)
  - [Example](#example)

## Objectives

* Log a list of PVs that update asynchronous to sample measurements.
* List should be a text file that is easy to read and load.
* text file should not be too long so make a new file for each day

## Required packages

* [ophyd](https://anaconda.org/conda-forge/ophyd) (from the Bluesky framework)
* Python 3.7+

## Notes

The [dhtioc](https://github.com/prjemian/dhtioc) project
has the [datalogger](https://github.com/prjemian/dhtioc/blob/main/dhtioc/datalogger.py)
module that was used as a starting point.

## Command-line help

Request command-line help: `pvlogger.py --help`

```
usage: pvlogger [-h] [--path PATH] [--period PERIOD] [--duration DURATION] [-v] pvnames [pvnames ...]

pvlogger: record EPICS PVs in text files

positional arguments:
pvnames              one or more EPICS PV names

optional arguments:
-h, --help           show this help message and exit
--path PATH          logging directory, default: /home/prjemian/Documents/pvlogger
--period PERIOD      recording period, default: 10 (s)
--duration DURATION  recording ends after this duration, default: 3600 (s)
-v, --verbose        logging verbosity (default=quiet, v=some, vv=all)
```

## Example

Record 4 PVs every 10 s for 30 s and store into
directory ``/tmp/log1``.  Command:

```sh
pvlogger.py \
    -vv \
    --path /tmp/log1 \
    --duration 30 \
    rpib4b1:{temperature,humidity} \
    gp:{UPTIME,datetime}
```

which showed this output:

```
[INFO 2021-06-26 16:50:22.359 81] PvLogger starting
[DEBUG 2021-06-26 16:50:22.359 84] Connecting PV rpib4b1:temperature
[DEBUG 2021-06-26 16:50:22.360 84] Connecting PV rpib4b1:humidity
[DEBUG 2021-06-26 16:50:22.360 84] Connecting PV gp:UPTIME
[DEBUG 2021-06-26 16:50:22.360 84] Connecting PV gp:datetime
[INFO 2021-06-26 16:50:22.360 92] directory: /tmp/log1
[INFO 2021-06-26 16:50:22.360 198] changing recording period from None to 10 (s)
[INFO 2021-06-26 16:50:22.360 207] Periodic recording thread starting...
[INFO 2021-06-26 16:50:22.361 295] recording for 30 s at 10 s intervals
[DEBUG 2021-06-26 16:50:22.361 211] Waiting for rpib4b1:temperature to connect
[DEBUG 2021-06-26 16:50:22.541 211] Waiting for rpib4b1:humidity to connect
[DEBUG 2021-06-26 16:50:22.590 213] All 4 PVs connected
[DEBUG 2021-06-26 16:50:22.590 137] Creating log file /tmp/log1/2021/06/2021-06-26.txt
[DEBUG 2021-06-26 16:50:22.625 179] 1624744222.59	27.79999996281083	99.9	20 days, 01:24:52	2021-06-26 21:50:22	2021-06-26 16:50:22.590380
[DEBUG 2021-06-26 16:50:32.802 179] 1624744232.65	27.799999992804203	99.9	20 days, 01:25:02	2021-06-26 21:50:32	2021-06-26 16:50:32.647088
[DEBUG 2021-06-26 16:50:42.725 179] 1624744242.63	27.799999998607674	99.9	20 days, 01:25:12	2021-06-26 21:50:42	2021-06-26 16:50:42.629535
[INFO 2021-06-26 16:50:52.453 222] Periodic recording thread exiting...
```

