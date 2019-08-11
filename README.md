# Steam Market History Exporter
Export the Steam Market history to a CSV file.

## Installation

- Install Python3
- Install the requirements `pip install -r requirements.txt`

## Configuration
Rename `auth.sample.json` as `auth.json` and set user agent and cookies values.

You can find the values by opening the steam market and using the Developer Tools to find the cookies values.

## Usage
To download all your Steam Market history run
```sh
./history.py
```
The first run will be slow since it has to download all the history.
Subsequent invocations will be faster since it will download the updates only.

To export the history to csv run
```sh
./export.py myhistory.csv
```
