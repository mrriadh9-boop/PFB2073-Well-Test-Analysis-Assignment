import docx

doc = docx.Document("PFB2073_WellTest_Report_APA.docx")

print("=== DEEP AUDIT: TASK 5 - PAGE HEADER & RUNNING HEAD & PAGE NUMBERS ===")

for s_idx, section in enumerate(doc.sections):
    header = section.header
    print(f"Section {s_idx} Header:")
    for p_idx, p in enumerate(header.paragraphs):
        print(f"  Paragraph {p_idx}: '{p.text}'")
        print(f"  Alignment: {p.alignment}")

        # Check runs
        for r_idx, r in enumerate(p.runs):
            print(f"    Run {r_idx}: text='{r.text}'")
        
        # Check XML for page number field
        p_xml = p._p.xml
        print("  Paragraph XML Snippet:")
        print(f"    {p_xml[:500]}...")
        
        has_running_head = "WELL TEST ANALYSIS ASSIGNMENT 2" in p.text
        has_page = "PAGE" in p_xml
        
        print(f"  Running head check: {'PASS' if has_running_head else 'FAIL'}")
        print(f"  Page number check (w:fldSimple or w:instrText with PAGE): {'PASS' if has_page else 'FAIL'}")

