def hello() -> str:
    return "Hello, World!"

def test_hello() -> None:
    assert hello() == "Hello, World!"

if __name__ == "__main__":
    test_hello()
    print("All tests passed.")