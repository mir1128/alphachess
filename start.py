import multiprocessing
import subprocess


def worker():
    subprocess.call(["E:\\myprojects\\alphachess\\venv\\Scripts\\python", "aiplay.py"])


if __name__ == "__main__":
    jobs = []
    for i in range(36):
        p = multiprocessing.Process(target=worker)
        jobs.append(p)
        p.start()