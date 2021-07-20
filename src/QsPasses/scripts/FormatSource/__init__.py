# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from os import path
import os
import logging
import subprocess


def discover_formatter():
    # TODO(TFR): Auto discover, use full path
    return "clang-format"


logger = logging.getLogger()
PROJECT_ROOT = path.abspath(path.dirname(path.dirname(path.dirname(__file__))))
CLANG_FORMAT_EXE = discover_formatter()

#######
# Style pipeline components


def require_token(token, filename, contents, cursor, dry_run):
    failed = False
    if not contents[cursor:].startswith(token):
        logger.error("{}: File must have {} at position {}".format(filename, token, cursor))
        failed = True
    return cursor + len(token), failed


def require_pragma_once(filename, contents, cursor, dry_run):
    return require_token("#pragma once\n", filename, contents, cursor, dry_run)


def require_todo_owner(filename, contents, cursor, dry_run):
    # TODO(tfr): implement
    return cursor, False


def enforce_cpp_license(filename, contents, cursor, dry_run):
    return require_token("""// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

""", filename, contents, cursor, dry_run)


def enforce_py_license(filename, contents, cursor, dry_run):
    # Allowing empty files
    if contents.strip() == "":
        return cursor, False

    return require_token("""# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

""", filename, contents, cursor, dry_run)


def enforce_formatting(filename, contents, cursor, dry_run):
    p = subprocess.Popen(
        [CLANG_FORMAT_EXE, '-style=file'],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        cwd=PROJECT_ROOT)
    output = p.communicate(input=contents.encode())[0]

    if p.returncode != 0:
        raise Exception('Could not format contents')

    formatted = output.decode('utf-8')
    if formatted != contents:
        logger.error("{} was not correctly formatted.".format(filename))

    return cursor, False


#######
# Source pipeline definitions


AUTO_FORMAT_LANGUAGES = [
    {
        "name": "C++ Main",
        "src": path.join(PROJECT_ROOT, "src"),

        "pipelines": {
            "hpp": [
                require_pragma_once,
                enforce_cpp_license,
                enforce_formatting
            ],
            "cpp": [
                enforce_cpp_license,
                enforce_formatting
            ]
        }
    },
    {
        "name": "Scripts",
        "src": path.join(PROJECT_ROOT, "scripts"),

        "pipelines": {
            "py": [
                enforce_py_license,
            ],
        }
    }
]


def execute_pipeline(pipeline, filename: str, dry_run: bool):
    logger.info("Executing pipeline for {}".format(filename))
    cursor = 0

    with open(filename, "r") as fb:
        contents = fb.read()

    failed = False
    for fnc in pipeline:
        cursor, f = fnc(filename, contents, cursor, dry_run)
        failed = failed or f

    return failed


def main(dry_run: bool = True):
    failed = False

    for language in AUTO_FORMAT_LANGUAGES:
        logger.info("Formatting {}".format(language["name"]))
        basedir = language["src"]
        pipelines = language["pipelines"]

        for root, dirs, files in os.walk(basedir):

            for filename in files:
                if "." not in filename:
                    continue

                _, ext = filename.rsplit(".", 1)
                if ext in pipelines:
                    f = execute_pipeline(pipelines[ext], path.join(root, filename), dry_run)
                    failed = failed or f

    if failed:
        logger.error("Your code did not pass formatting.")

    return failed


if __name__ == "__main__":
    if main():
        exit(-1)
