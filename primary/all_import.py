import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import json
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv
import logging
from typing import Dict, List, Optional, Any

# Import our portfolio analyzer
from kiteconnect import KiteConnect
import google.generativeai as genai
from dataclasses import dataclass

# Voice synthesis imports
import pyttsx3
import threading
from io import BytesIO
import base64



# Load environment variables at the top
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)