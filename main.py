from os import walk
import argparse


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


def isFunction(line: str) -> bool:
    if "func " in line and not line.rstrip().startswith("//"):
        return True
    return False


def getFunctionFromLine(line: str) -> (str, str):
    words = line.split(" ")
    if words[1].startswith("("):  # then this function is a class method
        func_name = words[3].split("(")[0].strip("(*)")
        class_name = words[2].strip('(*)')
    else:
        func_name = words[1].split("(")[0]
        class_name = ""
    return func_name, class_name


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
                function_name, class_name = getFunctionFromLine(lines[i])
                function_name = package + "." + function_name
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
                if function.name in lines[i]:
                    count[function] += 1
        f.close()
    return count


def print_results(path_: str, counts_: dict):
    for f in counts_:
        if counts_[f] == 0:
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
except:
    print("No such directory or can not get access")
    raise SystemExit(1)

go_files = read_files(path)
go_functions = read_functions(go_files)
counts = count_functions(go_files, go_functions)
print_results(path, counts)
