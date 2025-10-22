import pytesseract
from PIL import Image, ImageFilter, ImageOps
from io import BytesIO

def solve_captcha(browser, captcha_element):
    """
    Captures and solves CAPTCHA from the given browser and CAPTCHA element.
    Returns the cleaned CAPTCHA text with multiple OCR strategies.
    """
    try:
        # Get CAPTCHA image as PNG from the element
        captcha_png = captcha_element.screenshot_as_png
        original_image = Image.open(BytesIO(captcha_png))

        # Save original for debugging
        original_image.save("captcha_original.png")

        # Try multiple OCR strategies
        strategies = [
            # Strategy 1: Standard preprocessing
            {
                "name": "standard",
                "preprocess": lambda img: img.convert("L").point(lambda x: 0 if x < 140 else 255, '1'),
                "config": r'--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
            },
            # Strategy 2: No inversion (for light backgrounds)
            {
                "name": "no_invert", 
                "preprocess": lambda img: img.convert("L").point(lambda x: 0 if x < 120 else 255, '1').filter(ImageFilter.MedianFilter()),
                "config": r'--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
            },
            # Strategy 3: Different threshold
            {
                "name": "high_contrast",
                "preprocess": lambda img: img.convert("L").point(lambda x: 0 if x < 100 else 255, '1'),
                "config": r'--psm 6 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
            }
        ]

        best_result = ""
        
        for strategy in strategies:
            try:
                # Apply preprocessing
                processed_image = strategy["preprocess"](original_image.copy())
                processed_image.save(f"captcha_{strategy['name']}.png")
                
                # Run OCR
                captcha_text = pytesseract.image_to_string(processed_image, config=strategy["config"])
                captcha_text = captcha_text.strip().replace(" ", "").replace("\n", "")
                
                print(f"[OCR-{strategy['name']}] Result: '{captcha_text}' (length: {len(captcha_text)})")
                
                # Check if result looks valid (6 characters is typical for CPPP)
                if len(captcha_text) == 6 and captcha_text.isalnum():
                    print(f"✅ OCR SUCCESS with {strategy['name']} strategy")
                    return captcha_text
                elif len(captcha_text) >= 4:  # Keep best partial result
                    if len(captcha_text) > len(best_result):
                        best_result = captcha_text
                        
            except Exception as e:
                print(f"[OCR-{strategy['name']}] Failed: {e}")
                continue
        
        # If we have a partial result, use it
        if best_result and len(best_result) >= 4:
            print(f"⚠️ Using best OCR result: '{best_result}'")
            return best_result
            
        # Last resort: return empty to trigger retry logic
        print("❌ All OCR strategies failed")
        return ""
        
    except Exception as e:
        print(f"❌ Complete CAPTCHA solving error: {e}")
        return ""
