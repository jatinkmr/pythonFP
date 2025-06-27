import datetime
import random


def generateUniqueSixDigitToken():
    timestamp = int(datetime.datetime.now().timestamp() * 1000)
    random_number = random.randint(10000, 99999)
    unique_number = str(timestamp) + str(random_number)
    return unique_number[:15]
