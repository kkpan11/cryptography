# This file is dual licensed under the terms of the Apache License, Version
# 2.0, and the BSD License. See the LICENSE file in the root of this repository
# for complete details.

import pathlib
import re
import subprocess

import click
import tomllib
from packaging.version import Version


def run(*args: str) -> None:
    print(f"[running] {list(args)}")
    subprocess.check_call(list(args))


@click.group()
def cli():
    pass


@cli.command()
@click.argument("version")
def release() -> None:
    base_dir = pathlib.Path(__file__).parent
    with (base_dir / "pyproject.toml").open("rb") as f:
        pyproject = tomllib.load(f)
        version = pyproject["project"]["version"]

    if Version(version).is_prerelease:
        raise RuntimeError(
            f"Can't release, pyproject.toml version is pre-release: {version}"
        )

    # Tag and push the tag (this will trigger the wheel builder in Actions)
    run("git", "tag", "-s", version, "-m", f"{version} release")
    run("git", "push", "--tags", "git@github.com:pyca/cryptography.git")


def replace_version(
    p: pathlib.Path, variable_name: str, new_version: str
) -> None:
    content = p.read_text()

    pattern = rf"^{variable_name}\s*=\s*.*$"
    match = re.search(pattern, content, re.MULTILINE)
    assert match is not None

    start, end = match.span()
    new_content = (
        content[:start] + f'{variable_name} = "{new_version}"' + content[end:]
    )

    p.write_text(new_content)


@cli.command()
@click.argument("new_version")
def bump_version(new_version: str) -> None:
    base_dir = pathlib.Path(__file__).parent

    replace_version(base_dir / "pyproject.toml", "version", new_version)
    replace_version(
        base_dir / "src/cryptography/__about__.py", "__version__", new_version
    )
    replace_version(
        base_dir / "vectors/pyproject.toml",
        "version",
        new_version,
    )
    replace_version(
        base_dir / "vectors/cryptography_vectors/__about__.py",
        "__version__",
        new_version,
    )


if __name__ == "__main__":
    cli()
