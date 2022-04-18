import sys
from .mainwindowtk import MainFrameTk





def main(args = None):
    if args is None:
        args = sys.argv[1:]
    app = MainFrameTk()
    sys.exit(app.mainloop())


if __name__ == "__main__":
    main()