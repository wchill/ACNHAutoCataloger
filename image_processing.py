import cv2
import numpy as np
import pytesseract


POINTER_IMG = cv2.imread('./pointer.png', cv2.IMREAD_COLOR)
VARIATIONS_IMG = cv2.imread('./variations.png', cv2.IMREAD_COLOR)
VARIANT_IMG = cv2.imread('./variant.png', cv2.IMREAD_COLOR)


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


def find_pointer(image, match_method=4):
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

    print(matchLoc)
    slot = matchLoc[1] // 80
    return slot


def has_multiple_variants(image):
    text_min_x = 162
    text_min_y = 836
    text_max_x = 378
    text_max_y = 890

    templ = VARIATIONS_IMG
    cropped = image[text_min_y:text_max_y, text_min_x:text_max_x]

    return has_image(cropped, templ)


# https://stackoverflow.com/questions/29663764/determine-if-an-image-exists-within-a-larger-image-and-if-so-find-it-using-py
def has_image(im, tpl):
    im = np.atleast_3d(im)
    tpl = np.atleast_3d(tpl)
    H, W, D = im.shape[:3]
    h, w = tpl.shape[:2]

    # Integral image and template sum per channel
    sat = im.cumsum(1).cumsum(0)
    tplsum = np.array([tpl[:, :, i].sum() for i in range(D)])

    # Calculate lookup table for all the possible windows
    iA, iB, iC, iD = sat[:-h, :-w], sat[:-h, w:], sat[h:, :-w], sat[h:, w:]
    lookup = iD - iB - iC + iA
    # Possible matches
    possible_match = np.where(np.logical_and.reduce([lookup[..., i] == tplsum[i] for i in range(D)]))

    # Find exact match
    for y, x in zip(*possible_match):
        if np.all(im[y+1:y+h+1, x+1:x+w+1] == tpl):
            return True

    return False


def get_variant(image):
    box = (0, 930, 770, 1000)
    templ = VARIANT_IMG
    cropped = image[box[1]:box[3], box[0]:box[2]]
    if not has_image(cropped, templ):
        return None
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


def process_frame(image, slot=None, only_get_variant=False):
    if not only_get_variant:
        name = get_item_name(image, slot)
        has_variants = has_multiple_variants(image)
    else:
        name = None
        has_variants = True
    variant_name = get_variant(image)
    return name, has_variants, variant_name
