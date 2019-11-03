#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, session
import os
import sys

app = Flask(__name__)


app.secret_key = '\x18\x19\xc3q\xfa\xb8\x80v\x1abf\xd8\xfd%(G\x95\xd7\xae\x9bv\xb0d\xf4'
from app import routes
