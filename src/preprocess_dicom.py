import os
import pydicom
import numpy as np
import cv2
from tqdm import tqdm
from pydicom.pixel_data_handlers.util import apply_windowing
import pandas as pd


def is_dicom_file(filename):

    #判断某文件是否是dicom格式的文件
    file_stream = open(filename, 'rb')
    file_stream.seek(128)
    data = file_stream.read(4)
    file_stream.close()
    if data == b'DICM':
        return True
    return False
  
def linear_reflect(dcm_array,dcm_data):
  slope = dcm_data.RescaleSlope
  intercept = dcm_data.RescaleIntercept
  
  # set wc and ww by self wc(-450~-600) ww(1500,2000)
  wc = dcm_data.WindowCenter
  ww = dcm_data.WindowWidth

  lowest = wc-ww/2
  highest = wc+ww/2

  
  dcm_array = dcm_array*slope+intercept
  
  normalized_array = (dcm_array-dcm_array.min())/(dcm_array.max()-dcm_array.min())
  
  lowest = (lowest-dcm_array.min())/(dcm_array.max()-dcm_array.min())
  highest = (highest-dcm_array.min())/(dcm_array.max()-dcm_array.min())
  
  # Directly set values outside the window to 0 (or desired background value)
  normalized_array[normalized_array < lowest] = 0  # Set to black
  normalized_array[normalized_array > highest] = 1  # Set to white (or desired max value)
  
  normalized_array = normalized_array*255
  
  return normalized_array
  
def reflection(dcm_array,dcm_data,key):
  if key==1:
    windowed_array = apply_windowing(dcm_array,dcm_data)
    windowed_array = windowed_array-np.min(windowed_array)
    windowed_array = windowed_array/np.max(windowed_array)*255
    return windowed_array
  elif key==2:
    return linear_reflect(dcm_array,dcm_data)

def save_as_png(png_dic,dcm_root,array):
  dcm_name = os.path.basename(dcm_root)
  name,ext = os.path.splitext(dcm_name)
  if not os.path.exists(png_dic):
    os.makedirs(png_dic)
  cv2.imwrite(png_dic+'/'+name+".png",array)
  return png_dic+'/'+name+".png"
  
def translate_single_dicom(dcm_root,png_root):
  if not is_dicom_file(dcm_root):
    return '-1'
  
  # Read the DICOM file
  dcm_data = pydicom.read_file(dcm_root)
  sop = dcm_data.SOPInstanceUID
  dcm_array = dcm_data.pixel_array
  array = reflection(dcm_array,dcm_data,2)
  return save_as_png(png_root,dcm_root,array),sop

if __name__ == "__main__":
  csv_root = "../datafile.csv"

  df = pd.read_csv("../datafile.csv")
  df['Png']='-1'
  df['SOP']='-1'
  for index, row in tqdm(df.iterrows()):
    dcm_root = row['dicom']
    png_dir = dcm_root.replace("Data", "Png")
    png_dir = os.path.dirname(png_dir)
    png_root,sop = translate_single_dicom(dcm_root, png_dir)
    row['Png'] = png_root
    row['SOP'] = sop
    df.iloc[index] = row
  # Save the modified DataFrame to CSV (assuming 'csv_root' is defined)
  df.to_csv(csv_root, index=False)
