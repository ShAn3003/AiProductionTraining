import pandas as pd
import ast
import math

def load_csv(file_path):
    return pd.read_csv(file_path)

def parse_rectangles(rectangles_str):
    if pd.isna(rectangles_str):
        return None
    return ast.literal_eval(rectangles_str)

def calculate_center(rect):
    center_x = (rect['xmin'] + rect['xmax']) / 2
    center_y = (rect['ymin'] + rect['ymax']) / 2
    return (center_x, center_y)

def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def merge_rectangles(rects):
    if not rects:
        return None
    xmins = [rect['xmin'] for rect in rects]
    xmaxs = [rect['xmax'] for rect in rects]
    ymins = [rect['ymin'] for rect in rects]
    ymaxs = [rect['ymax'] for rect in rects]
    return {
        'xmin': min(xmins),
        'xmax': max(xmaxs),
        'ymin': min(ymins),
        'ymax': max(ymaxs)
    }

def process_targets(rectangles_list):
    if rectangles_list is None:
        return None
    centers = [calculate_center(rect) for rect in rectangles_list]
    merged_rectangles = []
    used = [False] * len(rectangles_list)

    for i in range(len(centers)):
        if used[i]:
            continue
        group = [rectangles_list[i]]
        used[i] = True
        for j in range(i + 1, len(centers)):
            if not used[j] and calculate_distance(centers[i], centers[j]) <= 30:
                group.append(rectangles_list[j])
                used[j] = True
        merged_rectangles.append(merge_rectangles(group))

    return merged_rectangles

def save_csv(data, file_path):
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)

def main(input_csv, output_csv):
    df = load_csv(input_csv)
    df['target'] = df['target'].apply(parse_rectangles)
    df['target'] = df['target'].apply(process_targets)
    save_csv(df, output_csv)

if __name__ == "__main__":
    input_csv_path = '../datafile.csv'  # 输入CSV文件路径
    output_csv_path = '../datafile.csv'  # 输出CSV文件路径
    main(input_csv_path, output_csv_path)
