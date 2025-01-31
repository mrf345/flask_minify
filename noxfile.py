import os

import nox

nox.options.sessions = ["lint", "test"]

basedir = os.path.abspath(os.path.dirname(__file__))
about_path = os.path.join(basedir, os.path.join("flask_minify", "about.py"))
about_content = ""
test_req_path = os.path.join("requirements", "test.txt")
dev_req_path = os.path.join("requirements", "dev.txt")

with open(about_path) as f:
    about_content = f.read()
    exec(about_content)  # nosec


@nox.session(python=__supported_versions__)  # type: ignore
def test(session: nox.session):
    session.install("-r", test_req_path)
    session.run("python", "-m", "pytest")
    session.run("python", "-m", "bandit", "-c", "bandit.yml", "-r", ".")


@nox.session
def lint(session: nox.Session):
    session.install("-r", test_req_path)
    session.run(
        "python", "-m", "isort", "-sg", "**/.nox*", "--profile", "black", "--check", "."
    )
    session.run("python", "-m", "black", "--check", ".")


@nox.session
def format(session: nox.Session):
    session.install("-r", test_req_path)
    session.run("python", "-m", "isort", "-sg", "**/.nox*", "--profile", "black", ".")
    session.run("python", "-m", "black", ".")


@nox.session
def release(session: nox.Session):
    session.install("-r", dev_req_path)
    session.run("python", "setup.py", "sdist", "bdist_wheel")
    session.run("python", "-m", "twine", "upload", "dist/*")
    session.run("rm", "-rf", "dist", "build", "Flask_Minify.egg-info", ".eggs")


@nox.session
def bump(session: nox.Session):
    old_version = __version__  # type: ignore
    new_version = old_version.split(".")
    new_version[-1] = str(int(new_version[-1]) + 1)
    new_version = ".".join(new_version)

    with open(about_path, "w") as f:
        f.write(about_content.replace(old_version, new_version))

    session.run("git", "add", about_path, external=True)
    session.run(
        "git", "commit", "-m", f"chore: bump version to {new_version}", external=True
    )
