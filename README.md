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
  - [Citations](#citations)

## Objectives

* Log a list of PVs that update asynchronous to sample measurements.
* List should be a text file that is easy to read and load.
* text file should not be too long so make a new file for each day

## Required packages

* [ophyd](https://anaconda.org/conda-forge/ophyd) (from the Bluesky framework)
* Python 3.7+

## Notes

When creating a log entry for the first time, this code will create all
necessary directories to store the log file.

If the log file exists for the current log entry, the new data will be appended
to that file (even if the list of PVs is different).

**IMPORTANT**: Keep in mind, if you change the list of PVs, you should point to
a different base directory to store your logs!

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

| option | meaning | verbosity
| ---    | ---     | ---
|        | quiet   | no output (except Python exceptions)
| `-v`   | some    | `INFO`-level messages
| `-vv`  | all     | ... and `DEBUG`-level messages

## Example

Record 4 PVs every 10 s for 30 s and store into
directory ``/tmp/log1``.  Command:

```sh
pvlogger.py \
    -vv \
    --path /tmp/log1 \
    --period 10 \
    --duration 30 \
    rpib4b1:{temperature,humidity} \
    gp:{UPTIME,datetime}
```

<details>
<summary>command line output:</summary>

Note:  Items inside the square brackets are:

* log level : such as `INFO`
* date and time : such as `2021-06-26 17:34:05.934`
* line number in `pylogger.py` : such as `79`

```
[INFO 2021-06-26 17:34:05.934 79] PvLogger starting
[DEBUG 2021-06-26 17:34:05.934 82] Connecting PV rpib4b1:temperature
[DEBUG 2021-06-26 17:34:05.935 82] Connecting PV rpib4b1:humidity
[DEBUG 2021-06-26 17:34:05.935 82] Connecting PV gp:UPTIME
[DEBUG 2021-06-26 17:34:05.935 82] Connecting PV gp:datetime
[INFO 2021-06-26 17:34:05.936 90] directory: /tmp/log1
[INFO 2021-06-26 17:34:05.936 196] changing recording period from None to 10 (s)
[INFO 2021-06-26 17:34:05.936 205] Periodic recording thread starting...
[INFO 2021-06-26 17:34:05.936 295] recording for 30 s at 10 s intervals
[DEBUG 2021-06-26 17:34:05.936 209] Waiting for rpib4b1:temperature to connect
[DEBUG 2021-06-26 17:34:06.145 209] Waiting for rpib4b1:humidity to connect
[DEBUG 2021-06-26 17:34:06.200 211] All 4 PVs connected
[DEBUG 2021-06-26 17:34:06.201 135] Creating log file /tmp/log1/2021/06/2021-06-26.txt
[DEBUG 2021-06-26 17:34:06.219 173] {'rpib4b1:temperature': {'value': 28.000000000170992, 'timestamp': 1624746845.9207}}
[DEBUG 2021-06-26 17:34:06.248 173] {'rpib4b1:humidity': {'value': 99.9, 'timestamp': 1624746845.908766}}
[DEBUG 2021-06-26 17:34:06.264 173] {'gp:UPTIME': {'value': '20 days, 02:08:36', 'timestamp': 1624746845.918983}}
[DEBUG 2021-06-26 17:34:06.265 173] {'gp:datetime': {'value': '2021-06-26 22:34:06', 'timestamp': 1624746846.219304}}
[DEBUG 2021-06-26 17:34:16.313 173] {'rpib4b1:temperature': {'value': 28.000000000033083, 'timestamp': 1624746855.917284}}
[DEBUG 2021-06-26 17:34:16.354 173] {'rpib4b1:humidity': {'value': 99.9, 'timestamp': 1624746855.905822}}
[DEBUG 2021-06-26 17:34:16.375 173] {'gp:UPTIME': {'value': '20 days, 02:08:46', 'timestamp': 1624746855.919137}}
[DEBUG 2021-06-26 17:34:16.377 173] {'gp:datetime': {'value': '2021-06-26 22:34:16', 'timestamp': 1624746856.31925}}
[DEBUG 2021-06-26 17:34:26.318 173] {'rpib4b1:temperature': {'value': 28.0000000000064, 'timestamp': 1624746865.919651}}
[DEBUG 2021-06-26 17:34:26.357 173] {'rpib4b1:humidity': {'value': 99.9, 'timestamp': 1624746865.907614}}
[DEBUG 2021-06-26 17:34:26.375 173] {'gp:UPTIME': {'value': '20 days, 02:08:56', 'timestamp': 1624746865.919137}}
[DEBUG 2021-06-26 17:34:26.376 173] {'gp:datetime': {'value': '2021-06-26 22:34:26', 'timestamp': 1624746866.319303}}
[INFO 2021-06-26 17:34:35.998 220] Periodic recording thread exiting...
```

</details>

<details>
<summary>log file:</summary>

```
# file: /tmp/log1/2021/06/2021-06-26.txt
# created: 2021-06-26 17:34:06.201412
# program: pvlogger
# column separator: tab (^T or \t)
#
# time: (UTC) seconds (since 1970-01-01T00:00:00 UTC)
# 
# time	rpib4b1:temperature	rpib4b1:humidity	gp:UPTIME	gp:datetime	ymd hms
1624746846.20	28.000000000170992	99.9	20 days, 02:08:36	2021-06-26 22:34:06	2021-06-26 17:34:06.200951
1624746856.29	28.000000000033083	99.9	20 days, 02:08:46	2021-06-26 22:34:16	2021-06-26 17:34:16.287332
1624746866.20	28.0000000000064	99.9	20 days, 02:08:56	2021-06-26 22:34:26	2021-06-26 17:34:26.203805
```

</details>

## Citations

The [dhtioc](https://github.com/prjemian/dhtioc) project
has the [datalogger](https://github.com/prjemian/dhtioc/blob/main/dhtioc/datalogger.py)
module that was used as a starting point.
