#!/usr/bin/env python3
"""Build the de-identified edition pages. Standard library only.

  python3 public-guide/_gen.py            # builds every page
  python3 public-guide/_gen.py index.py   # builds only the named modules
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

MODULES = [
    'p_index.py', 'p_decision.py', 'p_projections.py', 'p_blackswan.py', 'p_process.py',
    'p_law.py', 'p_costs.py', 'p_estate.py', 'p_questions.py', 'p_suggestions.py',
    'p_flagged.py', 'p_sources.py', 'p_requirements.py',
]


def run(name):
    path = os.path.join(HERE, name)
    spec = importlib.util.spec_from_file_location(name[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build()


def main(argv):
    wanted = [a if a.endswith('.py') else a + '.py' for a in argv[1:]] or MODULES
    built = []
    for name in MODULES:
        if name in wanted:
            built.append(run(name))
    print('built %d de-identified page(s): %s' % (len(built), ', '.join(built)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
