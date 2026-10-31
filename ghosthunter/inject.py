"""Fault injection for demo scenarios defined in the target file. Usage: python inject.py A|B|C|reset"""
import sys
import core

def inject(key):
    return core.inject(key)

if __name__ == "__main__":
    print("\n".join(inject(sys.argv[1])))
