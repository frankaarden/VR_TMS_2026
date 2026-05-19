import xml.etree.ElementTree as ET

# paths
xml_file1 = "path/reference_marker.xml"
xml_file2 = "path/acquired_marker.xml"

def get_coil_x(xml_file):
    root = ET.parse(xml_file).getroot()
    matrix = root.find('.//Matrix4D')
    return float(matrix.get('data03'))

x1 = get_coil_x(xml_file1)
x2 = get_coil_x(xml_file2)

print("X-axis displacement:", abs(x1 - x2), "mm")