import stl

def main() -> None:
    print(stl.open_stl_file("test.stl")["facet-count"])

if __name__ == "__main__":
    main()
