# Python Version: 3.x
import pathlib
import shlex
import subprocess
from logging import getLogger
from typing import *

from onlinejudge_verify.config import get_config
from onlinejudge_verify.languages.models import Language, LanguageEnvironment

logger = getLogger(__name__)


class NimLanguageEnvironment(LanguageEnvironment):
    NIMFLAGS: List[str]
    compile_to: str

    def __init__(self, *, NIMFLAGS, compile_to):
        self.NIMFLAGS = NIMFLAGS
        self.compile_to = compile_to

    def compile(self, path: pathlib.Path, *, basedir: pathlib.Path, tempdir: pathlib.Path) -> None:
        command = compile = ["nim", self.compile_to, "-p:.", "-d:release", "-o:{tempdir}/a.out".format(tempdir=str(tempdir)), ' '.join(self.NIMFLAGS), "{path}".format(path=str(path))]
        logger.info('$ %s', ' '.join(command))
        subprocess.check_call(shlex.split(command))

    def get_execute_command(self, path: pathlib.Path, *, basedir: pathlib.Path, tempdir: pathlib.Path) -> List[str]:
        command = execute = "{tempdir}/a.out".format(path=str(path), basedir=str(basedir), tempdir=str(tempdir))
        return shlex.split(command)


class NimLanguage(Language):
    config: Dict[str, Any]

    def __init__(self, *, config: Optional[Dict[str, Any]] = None):
        if config is None:
            self.config = get_config().get('languages', {}).get('nim', {})
        else:
            self.config = config

    def list_dependencies(self, path: pathlib.Path, *, basedir: pathlib.Path) -> List[pathlib.Path]:
        command = "sed 's/^include \"\\(.*\\)\"$/\\1/ ; t ; d' {path}".format(path=str(path), basedir=str(basedir))
        text = subprocess.check_output(shlex.split(command))
        dependencies = [path]
        for line in text.splitlines():
            print(line)
            dependencies.append(pathlib.Path(line.decode()))
        return dependencies

    def bundle(self, path: pathlib.Path, *, basedir: pathlib.Path) -> bytes:
        raise NotImplementedError 

    def is_verification_file(self, path: pathlib.Path, *, basedir: pathlib.Path) -> bool:
        return path.name.endswith("_test.nim")

    def list_environments(self, path: pathlib.Path, *, basedir: pathlib.Path) -> Sequence[NimLanguageEnvironment]:
        compile_to = "cpp"
        if "compileTo" in self.config:
            compile_to = self.config["compileTo"]
        NIMFLAGS = ""
        if "NIMFLAGS" in self.config:
            NIMFLAGS = self.config["NIMFLAGS"].split()
        return [NimLanguageEnvironment(NIMFLAGS=NIMFLAGS, compile_to=compile_to)]
