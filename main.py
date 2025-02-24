# Author: Isaac J. Boots

import gui
import multiprocessing


def main() -> None:
    app: gui.App = gui.App()
    app.run()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
