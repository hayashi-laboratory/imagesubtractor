#!/usr/bin/env python3
from subprocess import Popen

if __name__ == "__main__":
    try:
        proc = Popen(
            ["python3", "-c", "import imagesubtractor; imagesubtractor.run_app()"]
        )
        proc.communicate()
    except Exception as e:
        proc.kill()
    finally:
        proc.terminate()
