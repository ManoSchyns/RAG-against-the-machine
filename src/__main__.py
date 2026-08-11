from .indexing import index
import fire

if __name__ == "__main__":
    fire.Fire({
        "index": index
    })
