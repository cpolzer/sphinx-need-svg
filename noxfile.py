import nox
from nox import session

PYTHON_VERSIONS = ["3.10", "3.12"]
SPHINX_VERSIONS = ["7.4", "8.1"]
SPHINX_NEEDS_VERSIONS = ["2.1", "4.2", "5.1", "6.3.0", "8.0.0"]


def run_tests(session, sphinx, sphinx_needs):
    session.install(".[test]")
    session.run("pip", "install", f"sphinx=={sphinx}", silent=True)
    session.run("pip", "install", f"sphinx_needs=={sphinx_needs}", silent=True)
    session.run("uv", "run", "pytest", "tests/", "-v", external=True)


@session(python=PYTHON_VERSIONS)
@nox.parametrize("sphinx_needs", SPHINX_NEEDS_VERSIONS)
@nox.parametrize("sphinx", SPHINX_VERSIONS)
def tests(session, sphinx_needs, sphinx):
    run_tests(session, sphinx, sphinx_needs)
