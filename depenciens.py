# Standard library imports
import os
import base64

# Third-party imports
import cv2
import numpy as np
import pandas as pd
import mysql.connector
import streamlit as st
from PIL import Image
from tensorflow.keras.models import load_model #type: ignore

# Local application imports
from views import beranda, dataset, akurasi, klasifikasi
from config import (
    DB_HOST, 
    DB_USER, 
    DB_PASSWORD, 
    DB_NAME, 
    IMAGE_DIR_SEGAR, 
    IMAGE_DIR_TIDAK_SEGAR,
    LOGO_PATH
)
from model import classify_image
from utils import (
    get_recommendation,
    get_image_paths,
    get_accuracy_data
)