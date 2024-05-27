# Author: Isaac J. Boots

import gui


files_path:str = r"C:\Users\TruUser\Desktop\checker\files"
uncentered_path:str = r"C:\Users\TruUser\Desktop\checker\output\uncentered"
over_10_pi_path:str = r"C:\Users\TruUser\Desktop\checker\output\over_10_pi"
over_14_pi_path:str = r"C:\Users\TruUser\Desktop\checker\output\over_14_pi"
passed_path:str = r"C:\Users\TruUser\Desktop\checker\output\passed"
exceeds_max_length_path:str = r"C:\Users\TruUser\Desktop\checker\output\exceeds_max_length"

def main() -> None:
    app:gui.App = gui.App()
    app.run()

if __name__ == "__main__":
    main()
