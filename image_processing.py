import cv2
import sys
import pytesseract
from east import detect_text_in_box


POINTER_IMG = cv2.imread('./pointer.png', cv2.IMREAD_COLOR)


def get_item_name(image, slot=None):
    item_slot_x = 952
    item_slot_y_start = 235
    item_slot_height = 80
    text_width = 640
    text_height = 70

    if slot is None:
        slot = find_pointer(image)

    y = item_slot_y_start + item_slot_height * slot
    box = (item_slot_x, y, item_slot_x + text_width, y + text_height)
    return run_tesseract(image, box)


def find_pointer(image, match_method=cv2.TM_SQDIFF):
    pointer_min_y = 235
    pointer_max_y = 235 + 8 * 80
    pointer_min_x = 775
    pointer_max_x = 880

    templ = POINTER_IMG

    cropped = image[pointer_min_y:pointer_max_y, pointer_min_x:pointer_max_x]

    result = cv2.matchTemplate(cropped, templ, match_method)

    cv2.normalize(result, result, 0, 1, cv2.NORM_MINMAX, -1)

    _minVal, _maxVal, minLoc, maxLoc = cv2.minMaxLoc(result, None)

    if match_method == cv2.TM_SQDIFF or match_method == cv2.TM_SQDIFF_NORMED:
        matchLoc = minLoc
    else:
        matchLoc = maxLoc

    slot = matchLoc[1] // 80
    return slot


def has_multiple_variants(image):
    box = (165, 840, 165 + 200, 840 + 42)
    boxes = detect_text_in_box(image, box)
    return len(boxes) > 0


def get_variant(image):
    box = (50, 940, 50 + 770, 940 + 60)
    boxes = detect_text_in_box(image, box)
    if len(boxes) == 0:
        return None
    boxes.sort(key=lambda r: r[0])
    return run_tesseract(image, box)


def run_tesseract(image, box):
    startX, startY, endX, endY = box
    roi = image[startY:endY, startX:endX]

    # in order to apply Tesseract v4 to OCR text we must supply
    # (1) a language, (2) an OEM flag of 4, indicating that the we
    # wish to use the LSTM neural net model for OCR, and finally
    # (3) an OEM value, in this case, 7 which implies that we are
    # treating the ROI as a single line of text
    config = "-l eng --oem 1 --psm 7"
    return pytesseract.image_to_string(roi, config=config)


def process_frame(image, only_get_variant=False):
    if not only_get_variant:
        name = get_item_name(image)
        has_variants = has_multiple_variants(image)
    else:
        name = None
        has_variants = True
    variant_name = get_variant(image)
    return name, has_variants, variant_name
