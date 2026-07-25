import os
from PIL import Image

def verify_plots():
    print("=== VERIFYING PLOT IMAGES ===")
    plots = [
        "Problem1_LogLog_Diagnostic.png",
        "Problem1_SemiLog.png",
        "Problem2_LogLog_Diagnostic.png",
        "Problem2_Horner.png"
    ]
    for p in plots:
        full_p = os.path.join(r"C:\Users\60163\Downloads\PFB2073_Well_Test_Analysis_-_May_2026_1784922163", p)
        exists = os.path.exists(full_p)
        size = os.path.getsize(full_p) if exists else 0
        if exists:
            img = Image.open(full_p)
            width, height = img.size
            mode = img.mode
            print(f"Plot '{p}': Exists=True, Size={size} bytes, Dimensions={width}x{height}, Mode={mode}")
        else:
            print(f"Plot '{p}': Exists=False")

if __name__ == "__main__":
    verify_plots()
