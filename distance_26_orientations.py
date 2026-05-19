import xml.etree.ElementTree as ET
import numpy as np

# paths
xml_file1 = "path/reference_marker.xml"
xml_file2 = "path/acquired_marker.xml"

def read_coordinates(xml_file):
    root = ET.parse(xml_file).getroot()
    coords = []
    for marker in root.findall('.//Marker'):
        m = marker.find('Matrix4D')
        coords.append((float(m.get('data03')),
                       float(m.get('data13')),
                       float(m.get('data23'))))
    return coords

ref = read_coordinates(xml_file1)
acq = read_coordinates(xml_file2)

for i in range(26):
    s = i * 8
    ref_x = ref[s][0]
    displacements = []
    for j in range(8):
        d = abs(acq[s + j][0] - ref_x)
        displacements.append(d)
        print(f"Group {i+1}, orientation {j*45}°: {d:.4f} mm")
    print(f"Mean: {np.mean(displacements):.4f} mm")
    print(f"SD:   {np.std(displacements):.4f} mm\n")