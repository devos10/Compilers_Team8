def main():
    import sys
    from main import run
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            src = f.read()
    else:
        src = """int x = 10
int y;
"""

    run(src)

if __name__ == "__main__":
    main()
