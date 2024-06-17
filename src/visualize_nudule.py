import pandas as pd
import cv2 
import os

def draw_rectangles_on_image(image_path, target_areas):
	"""
	Reads an image, draws rectangles based on target areas, and displays the image.

	Args:
		image_path (str): Path to the image file.
		target_areas (list): A list of dictionaries containing target area information.
			Each dictionary should have 'xmin', 'xmax', 'ymin', and 'ymax' keys.

	Returns:
		array
	"""

	try:
		img = cv2.imread(image_path)  # Read image
		if img is None:
			print(f"Error: Could not read image from '{image_path}'.")
			return

		# Check if target areas list is empty or has invalid entries
		if not target_areas:
			print(f"Warning: No target areas found for image '{image_path}'.")
			return
		for area in target_areas:
			if not all(key in area for key in ('xmin', 'xmax', 'ymin', 'ymax')):
				print(f"Warning: Invalid target area format in image '{image_path}'.")
				continue  # Skip drawing for this area

		# Draw rectangles
		for area in target_areas:
			xmin = int(area['xmin'])
			xmax = int(area['xmax'])
			ymin = int(area['ymin'])
			ymax = int(area['ymax'])
			cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)  # Draw green rectangles

	except Exception as e:
		print(f"Error: An unexpected error occurred: {e}")
	return img


if __name__ == "__main__":
  csv_root = "../datafile.csv"

  df = pd.read_csv(csv_root)

  visual_df = df[df['target'].notnull()]  # Select rows with non-null 'target' values

  visual_root = "../visualize_combined"

  for index, row in visual_df.iterrows():
    if not os.path.exists(visual_root):
      os.makedirs(visual_root)
    image_path = row['Png'].replace('\\','/')  # Assuming 'Png' is the image column name
    target_areas_str = row['target']
    target_areas = eval(target_areas_str)  # Assuming 'target' is a list of dictionaries
    img_with_blocks = draw_rectangles_on_image(image_path, target_areas)
    dcm_root = os.path.basename(row['dicom'])
    dcm_name,ext = os.path.splitext(dcm_root)
    visual_path = os.path.join(visual_root,dcm_name+"_vis.png")
    cv2.imwrite(visual_path,img_with_blocks)
		