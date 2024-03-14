import requests
import time


# this is chronjob which hits the liveness endpoint automatically

def distribute_job():
    print("all is well")
    print("need to mark distributed..")
    ...


if __name__ == "__main__":
    while True:
        distribute_job()
        time.sleep(2)