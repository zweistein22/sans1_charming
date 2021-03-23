import sys
import os
import importlib.util
import importlib.machinery


def main():
    os.environ["INSTRUMENT"] = "nicos_mlz.sans1_charming"
    print("INSTRUMENT=" + os.environ["INSTRUMENT"])
    argmusthave = "--other-instruments"
    if argmusthave not in sys.argv:
        sys.argv.append(argmusthave)

    nicos_root = os.path.normpath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    startupfile = "nicos-demo"
    reldir = "bin"
    dname = os.path.join(nicos_root,reldir)
    os.chdir(dname)
    print("running in dir: " + dname)
    fullpath = os.path.join(dname,startupfile)


    modulename = os.path.splitext(startupfile)[0]
    importlib.machinery.SOURCE_SUFFIXES.append('') # empty string to allow any file
    spec = importlib.util.spec_from_file_location(modulename, fullpath)
    python_code = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(python_code)


def run():
    sys.exit(main())

