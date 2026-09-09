import os
import sys

if __name__ == "__main__":
    # The package lives in <extension>/lib (see issue #486).
    lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
    if lib_dir not in sys.path:
        sys.path.insert(0, lib_dir)
    from sd_ui_dynamic_prompts.version_tools import install_requirements

    install_requirements(force=("-f" in sys.argv))
