# BUILD A WELL STURCUTRED SYSTEM TO DETECT 肺部结节 BASE ON THE CT IMAGE -- NORTHEAST UNIVERSITY ShAn_3003
## THOUGHT AND STEP
### Step01
* 数据整理：将对应的dcmi图片和对应的xml文件路径写入csv文件中方便下一步处理：generate_csv.ipynb  （为什么1号病人的study1里面的00000文件夹下面的dcmi这么少，也没有68.xml对应的dcmi）
* dcmi文件处理：后续需要学习一下dcmi文件如何转化到jpg图片（不同公司的窗宽、窗位不同）preprocess_dcmi.ipynb *发现采用了窗宽窗位优化效果不好，在0001号数据集上，直接对应变换更好*
* dcmi Problem:使用simpleITK和pydicom读出来的图片可视化之后效果不同，应该选择哪种

<div style="display: flex; justify-content: space-between;">
  <img src="./image/SimpleITK.png" alt="SimpleITK" style="width: 25%; height: 25%;">
  <img src="./image/MineCode.png" alt="My Own Code" style="width: 25%; height: 25%;">
  <img src="./image/Don'tProcess.png" alt="Don't Process" style="width: 25%; height: 25%;">
</div>

****
```python
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
```
![The Best Performance](./image/000069_key2.png)
****
### 自己理解：
ct扫描出来的图像数据在-1024-32768 而dicom文件存储一般用12位 所以要得到原始的ct数据，需要做一个线性变换来得到原始数据 即HU值

对于HU值，由于我们只关注肺部组织反映出来的HU值，所以将肺部组织之外的HU值设置为0
### Gemini:
In DICOM (Digital Imaging and Communications in Medicine) images, the attributes Slope, Intercept, WindowWidth, and WindowCenter play crucial roles in accurately displaying and interpreting the image data. Let's delve into their specific functions:

1. Slope (RescaleSlope):

The Slope attribute, also known as RescaleSlope, represents the factor by which the pixel values in the DICOM image need to be multiplied to obtain the actual physical values. It's analogous to the slope of a linear relationship between the pixel values and the corresponding physical quantities.

For instance, in a CT scan, the pixel values might represent Hounsfield Units (HU), which indicate the tissue density. The Slope value would then translate these pixel values into the actual HU values.

2. Intercept (RescaleIntercept):

The Intercept attribute, also known as RescaleIntercept, represents the constant value that needs to be added to the pixel values after multiplying them by the Slope. It acts as a baseline or offset for the pixel intensities.

Continuing with the CT scan example, the Intercept would adjust the HU values to ensure they fall within the appropriate range for displaying the image correctly.

3. WindowWidth (WindowWidth):

The WindowWidth attribute specifies the width of the grayscale window used to display the DICOM image. It determines the range of pixel values that will be mapped to the full range of display values (typically 0-255 for grayscale images).

A narrower WindowWidth will focus on a smaller range of pixel values, highlighting subtle variations within that range. Conversely, a wider WindowWidth will encompass a broader range of pixel values, providing a more general view of the image.

4. WindowCenter (WindowCenter):

The WindowCenter attribute defines the center of the grayscale window used for display. It determines the midpoint of the pixel value range that will be mapped to the full range of display values.

A higher WindowCenter will shift the window towards brighter pixel values, while a lower WindowCenter will shift it towards darker values. This allows for adjusting the display to emphasize specific features or structures within the image.

In summary, the Slope, Intercept, WindowWidth, and WindowCenter attributes work together to transform the raw pixel values in a DICOM image into a meaningful grayscale representation that can be accurately displayed and interpreted by medical professionals. They play a vital role in ensuring the correct visualization and analysis of medical imaging data.
****
****
* xml文件处理：对标注的结节区域转化成对应模型需要的数据格式（暂时针对yolo模型部署）最后还是得要本地部署（怎么解决这个问题）