import logging

logging.basicConfig(format='%(thread)d - %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',level=logging.INFO,
)
myprint = logging.info