from os import walk
import argparse
import re


class GoFunction:
    def __init__(self, name, file, row, package, struct=""):
        self.name = name
        self.file = file
        self.row = row
        self.type = struct
        self.package = package

    def __str__(self):
        return "function " + self.name


def read_files(path_: str) -> list:
    files = []
    for (dirpath, dirnames, filenames) in walk(path_):
        for file in filenames:
            if str(file).endswith(".go") and not str(file).endswith("_test.go"):
                files.append(dirpath + "\\" + file)
    return files


def getPackage(line: str) -> str:
    if "package" in line:
        return line.split()[1]
    return ""


def isFunction(line: str):
    return re.search(r"^\s*func", line)


def getFunctionFromLine(line: str) -> list:
    res1 = re.findall(r"^func \(\w+\s+\*\s*(\w*)\s*\)\s*(\w+).*\s*{$", line)
    res2 = re.findall(r"^()func ([^(]\w*).*\s*{$", line)
    if len(res2) == 0:
        return res1
    return res2


def read_functions(files: list) -> list:
    functions = []
    for file in files:
        f = open(file, "r", encoding="utf8")
        lines = f.read().split('\n')
        package = ""
        for i in range(len(lines)):
            if getPackage(lines[i]) != "":
                package = getPackage(lines[i])
            if isFunction(lines[i]):
                info = getFunctionFromLine(lines[i])
                class_name, function_name = info[0][0], info[0][1]
                functions.append(GoFunction(function_name, file, i + 1, package, class_name))
        f.close()
    return functions


def count_functions(files: list, functions: list) -> dict:
    count = dict()
    for function in functions:
        count[function] = -1
    for file in files:
        f = open(file, "r", encoding="utf8")
        lines = f.read().split('\n')
        for i in range(len(lines)):
            for function in functions:
                # MID TODO: work with function with identical names but different packages
                #       Now program does not distinguish between different functions from different packages
                if re.search(f"{function.name}", lines[i]):
                    count[function] += 1
        f.close()
    return count


def print_results(path_: str, counts_: dict):
    for f in counts_:
        if counts_[f] < 1:
            print(f"Function {f.name} defined in {f.file[len(path_):]}:{f.row} is not used")


parser = argparse.ArgumentParser(description='A tutorial of GUFF')
parser.add_argument("--path", help="Path to the directory to search unused functions", type=str, required=True)
args = parser.parse_args()

# MID TODO: work with functions with equal names, but different class.
#       Now program does not know method of which class is called (this is really bad)
# MIN TODO: work with different modules.
#       Now if function called from one of modules, it is called in all another (this is not good)
path = args.path
try:
    next(walk(path))
except Exception:
    print("No such directory or can not get access")
    raise SystemExit(1)

go_files = read_files(path)
go_functions = read_functions(go_files)
counts = count_functions(go_files, go_functions)
print_results(path, counts)
