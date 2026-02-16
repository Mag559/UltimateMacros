import logging
from console_prompt import main


if __name__ == "__main__":
    logging.basicConfig(filename='myapp.log', level=logging.DEBUG)
    main()
