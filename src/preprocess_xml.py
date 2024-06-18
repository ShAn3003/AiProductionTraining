import xml.etree.ElementTree as ET
import pandas as pd
from tqdm import tqdm

def analyze_xml(xml_root):
    """Parses an XML file and extracts data about unblinded read nodules.

    Args:
        xml_root (str): Path to the XML file.

    Returns:
        dict: A dictionary with SOP instance UIDs as keys and lists of edge
              dictionaries (containing bounding box coordinates) as values.
              If no relevant data is found, an empty dictionary is returned.
    """

    xmlns = '{http://www.nih.gov}'
    try:
        tree = ET.parse(xml_root)
    except FileNotFoundError:
        print(f"Error: XML file not found at '{xml_root}'.")
        return {}
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return {}

    reading_sessions = tree.findall(xmlns + 'readingSession')
    if not reading_sessions:
        return {}

    dcm_nodules = {}
    for reading_session in reading_sessions:
        unblinded_read_nodules = reading_session.findall(xmlns + 'unblindedReadNodule')
        if not unblinded_read_nodules:
            continue

        for nodule in unblinded_read_nodules:
            rois = nodule.findall(xmlns + 'roi')
            for roi in rois:
                try:
                    sop = roi.findall(xmlns + 'imageSOP_UID')[0].text
                except IndexError:
                    print("Warning: SOP_UID not found in ROI.")
                    continue

                edge_x = []
                edge_y = []
                for point in roi.findall(xmlns + 'edgeMap'):
                    try:
                        x = int(point.findall(xmlns + 'xCoord')[0].text)
                        y = int(point.findall(xmlns + 'yCoord')[0].text)
                    except (ValueError, IndexError):
                        print(f"Warning: Invalid coordinates in ROI for SOP '{sop}'.")
                        continue
                    edge_x.append(x)
                    edge_y.append(y)

                if edge_x and edge_y:
                    x_max, x_min, y_max, y_min = max(edge_x), min(edge_x), max(edge_y), min(edge_y)
                    edge = {
                        "xmax": x_max,
                        "ymax": y_max,
                        "xmin": x_min,
                        "ymin": y_min
                    }
                    if sop not in dcm_nodules:
                        dcm_nodules[sop] = [edge]
                    else:
                        dcm_nodules[sop].append(edge)

    return dcm_nodules

if __name__ == '__main__':
    csv_root = '../datafile.csv'
    try:
        df = pd.read_csv(csv_root)
    except FileNotFoundError:
        print(f"Error: CSV file not found at '{csv_root}'.")
        exit()
    except pd.errors.EmptyDataError:
        print(f"Error: CSV file '{csv_root}' is empty.")
        exit()
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        exit()

    df['target'] = None
    xml_root = None
    dcm_nodules = None
    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
        try:
            if xml_root != row['xml']:
                xml_root = row['xml']
                dcm_nodules = analyze_xml(xml_root)
            
            sop = row['SOP']
            if sop in dcm_nodules:
                df.at[index, 'target'] = dcm_nodules[sop]
            else:
                df.at[index, 'target'] = None
        except KeyError as e:
            print(f"Warning: Missing expected column {e} in CSV row {index}.")
            df.at[index, 'target'] = None
        except Exception as e:
            print(f"Error processing row {index}: {e}")
            df.at[index, 'target'] = None

    try:
        df.to_csv(csv_root, index=False)
    except Exception as e:
        print(f"Error writing to CSV file: {e}")
