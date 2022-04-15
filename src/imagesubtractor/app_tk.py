import sys
from imagesubtractor.mainwindowtk import MainFrameTk
import cv2





def main(args = None):
    if args is None:
        args = sys.argv[1:]
    cv2.startWindowThread()
    app = MainFrameTk()
    sys.exit(app.mainloop())


if __name__ == "__main__":
    main()