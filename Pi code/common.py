import cv2
import subprocess
from ultralytics import YOLO
import threading
import time


import serial
import json
import csv
import datetime as dt
import os

import asyncio
import sys
import logging
import sqlite3
from telethon import TelegramClient, events, Button



def date_time():
    now = dt.datetime.now()
    current_time = now.strftime("%I:%M:%S %p")
    current_date = dt.date.today()
    return current_date, current_time
