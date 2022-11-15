import os

def func(path):
    if not os.path.isdir(path):
        os.makedirs(path)

if __name__ == '__main__':
    print(" ") 