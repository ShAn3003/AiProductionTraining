import os
import pandas as pd


def remove_dir_suffix(file_or_dir_list):
    """
    Filters out entries that end with "dir" (assuming directory suffixes).

    Args:
        file_or_dir_list: List of filenames or directory names.

    Returns:
        List containing entries without the "dir" suffix.
    """
    return [element for element in file_or_dir_list if not element.endswith("dir")]


def get_specify_suffix(file_list, matching_suffix):
    """
    Filters a list of files based on a specified suffix.

    Args:
        file_list: List of filenames.
        matching_suffix: The suffix to filter by (e.g., "dcm", "xml").

    Returns:
        List containing entries with the matching suffix.
    """
    return [element for element in file_list if element.endswith(matching_suffix)]


def process_data_directory(data_dir):
    """
    Processes a medical data directory, extracts DICOM-XML pairs, and saves them to a CSV.

    Args:
        data_dir: Path to the data directory.

    Returns:
        None (saves results to a CSV file).
    """

    target_list = []
    label_list = []

    for patient in os.listdir(data_dir):
        patient_root = os.path.join(data_dir, patient)
        study_lists = os.listdir(patient_root)
        study_lists = remove_dir_suffix(study_lists)

        for study in study_lists:
            study_root = os.path.join(patient_root, study)
            series_lists = os.listdir(study_root)
            series_lists = remove_dir_suffix(series_lists)

            for series in series_lists:
                series_root = os.path.join(study_root, series)
                file_list = os.listdir(series_root)
                file_list = remove_dir_suffix(file_list)

                dcmi_lists = get_specify_suffix(file_list, "dcm")
                xml_lists = get_specify_suffix(file_list, "xml")

                if len(dcmi_lists)<=20:
                    continue
                if len(xml_lists)==1:
                    xml_root = os.path.join(series_root,xml_lists[0])
                    for dcmi in dcmi_lists:
                        dcmi_root = os.path.join(series_root, dcmi)
                        target_list.append(dcmi_root)
                        label_list.append(xml_root)
                else:  
                    for dcmi in dcmi_lists:
                        dcmi_root = os.path.join(series_root, dcmi)
                        index_d, _ = os.path.splitext(dcmi)
                        index_d = int(index_d)
                        xml_root = "-1"

                        for xml in xml_lists:
                            index_x, _ = os.path.splitext(xml)
                            index_x = int(index_x)
                            if index_x == index_d:
                                xml_root = os.path.join(series_root, xml)
                                break

                        target_list.append(dcmi_root)
                        label_list.append(xml_root)

    original_df = pd.DataFrame({"dicom": target_list, "xml": label_list})
    original_df.to_csv("../datafile.csv", index=False)


if __name__ == "__main__":
    data_dir = "E:/LIDC-IDRI"
    process_data_directory(data_dir)