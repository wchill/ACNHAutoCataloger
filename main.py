import cv2
import json
import sys
from image_processing import process_frame, get_item_name
import controller
from item import Item


def main(port):
    capture = cv2.VideoCapture(0)
    if not capture.isOpened():
        print('Error opening camera')
        sys.exit(1)

    # Init controller
    ctrl = controller.Controller(port)

    # Make the switch recognize this controller
    ctrl.press_button(controller.BTN_A)
    ctrl.p_wait(1)

    # Exit Change Grip/Order screen
    ctrl.press_button(controller.BTN_A)
    ctrl.p_wait(1)

    # Exit Controllers screen
    ctrl.press_button(controller.BTN_B)
    ctrl.p_wait(1)

    # Resume AC
    ctrl.press_button(controller.BTN_HOME)
    ctrl.p_wait(1)

    # We should be on the "Welcome to Nook Shopping!" screen
    # Make sure the cursor is in a known place
    ctrl.press_button(controller.DPAD_D)
    ctrl.press_button(controller.DPAD_L)
    ctrl.press_button(controller.DPAD_L)
    ctrl.press_button(controller.DPAD_L)

    # Open catalog
    ctrl.press_button(controller.BTN_A)
    ctrl.p_wait(1)

    # Get furniture
    furniture = process_screen(ctrl, capture)
    with open('furniture.json', 'w') as f:
        json.dump(furniture, f, default=lambda o: o.__dict__)

    # Get clothing
    ctrl.press_button(controller.DPAD_R)
    ctrl.press_button(controller.BTN_A)
    clothing = process_screen(ctrl, capture)
    with open('clothing.json', 'w') as f:
        json.dump(clothing, f, default=lambda o: o.__dict__)

    # Get wallpaper
    ctrl.press_button(controller.DPAD_R)
    ctrl.press_button(controller.BTN_A)
    ctrl.p_wait(1)
    wallpaper = process_screen(ctrl, capture)
    with open('wallpaper.json', 'w') as f:
        json.dump(wallpaper, f, default=lambda o: o.__dict__)

    capture.release()


def process_screen(ctrl, capture):
    # Scroll all the way up
    first_item = None
    while True:
        _, frame = capture.read()
        item = get_item_name(frame, 0)
        if first_item == item:
            break
        first_item = item
        ctrl.press_button(controller.RSTICK_U)
        # ctrl.p_wait(0.2)

    ctrl.press_button(controller.RSTICK_U)
    ctrl.p_wait(0.2)

    items = {}
    while True:
        _, frame = capture.read()
        res = process_item(ctrl, capture, items)
        if res is None:
            break
        print(res)
        items[res.name] = res
        ctrl.press_button(controller.DPAD_D)
        ctrl.p_wait(0.3)
    return list(items.values())


def process_item(ctrl, capture, processed_items):
    _, frame = capture.read()
    item_name, has_variants, variant_name = process_frame(frame)
    if item_name in processed_items:
        return None
    item = Item(item_name)
    if has_variants:
        while not item.has_variant(variant_name):
            item.add_variant(variant_name)
            ctrl.press_button(controller.BTN_X)
            # ctrl.p_wait(0.2)
            _, frame = capture.read()
            _, _, variant_name = process_frame(frame, only_get_variant=True)
    elif variant_name is not None:
        item.add_variant(variant_name)
    return item


def reset_controller(ctrl=None):
    if ctrl is None:
        ctrl = controller.Controller('COM6')

    ctrl.press_button(controller.BTN_B)

    ctrl.press_button(controller.BTN_HOME)
    ctrl.p_wait(1)
    ctrl.press_button(controller.DPAD_D)
    ctrl.press_button(controller.DPAD_R)
    ctrl.press_button(controller.DPAD_R)
    ctrl.press_button(controller.DPAD_R)
    ctrl.press_button(controller.BTN_A)
    ctrl.p_wait(1)
    ctrl.press_button(controller.BTN_A)
    return ctrl


if __name__ == '__main__':
    # main(sys.argv[1])
    main('COM6')
