from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import nox

nox.options.error_on_missing_interpreters = True
nox.options.reuse_existing_virtualenvs = True
nox.options.default_venv_backend = "uv"

ROOT = Path(__file__).parent
PYPROJECT_TOML_PATH = ROOT / "pyproject.toml"
TESTS_DIR = ROOT / "tests"
PYTEST_ENVX_DIR = ROOT / "src" / "pytest_envx"
NOXFILE_PATH = ROOT / "noxfile.py"

PYPROJECT_TOML = nox.project.load_toml("pyproject.toml")
PYTHON_VERSIONS = nox.project.python_versions(PYPROJECT_TOML)

PACKAGE = "pytest_envx"

TEST_DEPENDENCIES = nox.project.dependency_groups(PYPROJECT_TOML, "test")
TYPE_HINTS_DEPENDENCIES = nox.project.dependency_groups(PYPROJECT_TOML, "type_hints")
LINT_DEPENDENCIES = nox.project.dependency_groups(PYPROJECT_TOML, "lint")
PKG_META_DEPENDENCIES = nox.project.dependency_groups(PYPROJECT_TOML, "pkg-meta")


@dataclass(frozen=True, slots=True)
class EnvConfig:
    junit_xml: str
    coverage_xml: str
    coverage_html: str
    coverage_file: str
    diff_against: str
    xdist_workers: str

    @classmethod
    def from_env(cls, env_location: Path) -> EnvConfig:
        return cls(
            junit_xml=os.getenv("JUNIT_XML", str(env_location / "junit.xml")),
            coverage_xml=os.getenv("COVERAGE_XML", str(env_location / ".coverage.xml")),
            coverage_html=os.getenv("COVERAGE_HTML", str(env_location / "htmlcov")),
            coverage_file=os.getenv("COVERAGE_FILE", str(env_location / ".coverage")),
            diff_against=os.getenv("DIFF_AGAINST", "origin/master"),
            xdist_workers=os.getenv("PYTEST_XDIST_AUTO_NUM_WORKERS", "auto"),
        )


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    env_location = Path(session.virtualenv.location)
    config = EnvConfig.from_env(env_location)
    session.log("EnvConfig: %s", config)

    session.env["COVERAGE_FILE"] = config.coverage_file

    session.install(*TEST_DEPENDENCIES)
    session.install(".")  # Download as package

    # fmt: off
    session.run(
        "pytest",
        "-p", "no:pytest_envx",
        "-v",
        "-n", config.xdist_workers,
        "--junitxml", config.junit_xml,
        "--no-cov-on-fail",
        "--cov", PACKAGE,
        "--cov", TESTS_DIR,
        "--cov-config", PYPROJECT_TOML_PATH,
        "--cov-context", "test",
        "--cov-report", "term-missing",
        "--cov-report", f"html:{config.coverage_html}",
        "--cov-report", f"xml:{config.coverage_xml}",
    )

    session.run(
        "diff-cover",
        "--compare-branch", config.diff_against,
        config.coverage_xml,
    )
    # fmt: on


@nox.session
def lint(session: nox.Session) -> None:
    session.install(*LINT_DEPENDENCIES)
    session.run("pre-commit", "run", "--all-files", "--show-diff-on-failure")


@nox.session
def type_hints(session: nox.Session) -> None:
    session.install(*TYPE_HINTS_DEPENDENCIES)
    session.run("mypy", "--config", PYPROJECT_TOML_PATH, PYTEST_ENVX_DIR, TESTS_DIR, NOXFILE_PATH)


@nox.session
def pkg_meta(session: nox.Session) -> None:
    session.install(*PKG_META_DEPENDENCIES)

    tmp_dir = Path(session.create_tmp())

    session.run("uv", "build", "--sdist", "--wheel", "--out-dir", tmp_dir, ".")
    session.run("twine", "check", tmp_dir / "*")
    session.run("check-wheel-contents", "--no-config", tmp_dir)
