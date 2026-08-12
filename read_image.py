#!/usr/bin/env python3
import argparse
import os
import sys
import cv2
from image_utils import load_image, resize_image, to_grayscale, save_image

def parse_args():
    parser = argparse.ArgumentParser(description="Load, process, display, and optionally save an image.")
    parser.add_argument("--path", required=True, help="Path to the input image file.")
    parser.add_argument("--width", type=int, help="Target width for resizing.")
    parser.add_argument("--height", type=int, help="Target height for resizing.")
    parser.add_argument("--grayscale", action="store_true", help="Convert image to grayscale.")
    parser.add_argument("--save", help="File path to write the processed image.")
    return parser.parse_args()

def main():
    args = parse_args()

    if not os.path.isfile(args.path):
        print(f"Error: File not found – {args.path}", file=sys.stderr)
        sys.exit(1)

    try:
        img = load_image(args.path)
    except Exception as e:
        print(f"Error loading image: {e}", file=sys.stderr)
        sys.exit(1)

    if args.width and args.height:
        try:
            img = resize_image(img, args.width, args.height)
        except Exception as e:
            print(f"Error resizing image: {e}", file=sys.stderr)
            sys.exit(1)

    if args.grayscale:
        try:
            img = to_grayscale(img)
        except Exception as e:
            print(f"Error converting to grayscale: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        cv2.imshow("Image Viewer", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except cv2.error as e:
        print(f"OpenCV display error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.save:
        try:
            save_image(img, args.save)
        except Exception as e:
            print(f"Error saving image: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
