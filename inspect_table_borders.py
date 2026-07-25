import docx

doc = docx.Document("PFB2073_WellTest_Report_APA.docx")

for idx, table in enumerate(doc.tables):
    print(f"=== TABLE {idx+1} BORDER XML DETAILS ===")
    for r_idx, row in enumerate(table.rows):
        for c_idx, cell in enumerate(row.cells):
            tcPr = cell._tc.tcPr
            tcBorders = tcPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tcBorders') if tcPr is not None else None
            if tcBorders is not None:
                borders_str = []
                for b_child in tcBorders:
                    tag = b_child.tag.split('}')[-1]
                    val = b_child.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', b_child.attrib.get('val'))
                    sz = b_child.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sz', b_child.attrib.get('sz'))
                    color = b_child.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}color', b_child.attrib.get('color'))
                    borders_str.append(f"{tag}: val={val}, sz={sz}, color={color}")
                print(f"  Row {r_idx} Col {c_idx}: {borders_str}")
            else:
                print(f"  Row {r_idx} Col {c_idx}: No tcBorders on cell")

