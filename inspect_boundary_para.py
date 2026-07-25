import docx

doc = docx.Document("PFB2073_WellTest_Report_APA.docx")

for idx, p in enumerate(doc.paragraphs):
    if "nearest boundary distance" in p.text:
        print(f"Paragraph {idx+1}: {repr(p.text)}")
