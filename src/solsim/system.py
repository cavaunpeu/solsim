from abc import ABC, abstractmethod
import psutil
import signal
import subprocess
from subprocess import DEVNULL
import tempfile
from typing import Awaitable, Dict, Optional, Set, List, Any, Union

from anchorpy import create_workspace, close_workspace
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc import commitment

from solsim.type import StateType


class BaseSystem(ABC):
    @abstractmethod
    def initialStep(self) -> Awaitable[Any]:
        raise NotImplementedError

    @abstractmethod
    def step(self, state: StateType, history: List[StateType]) -> Awaitable[Any]:
        raise NotImplementedError


class BaseSolanaSystem(BaseSystem):

    SOLANA_CLUSTER_URI = "http://127.0.0.1:8899"

    def __init__(self, workspace_dir: str, client: Optional[Client] = None) -> None:
        self.logfile = tempfile.NamedTemporaryFile()
        self.localnet = subprocess.Popen(['anchor', 'localnet'], cwd=workspace_dir, stdout=self.logfile, stderr=DEVNULL)
        self.workspace = create_workspace(workspace_dir)
        self.client = client or Client(self.SOLANA_CLUSTER_URI)

    async def tearDown(self) -> None:
        await close_workspace(self.workspace)
        self._terminate_localnet()

    def get_token_account_balance(
        self, pubkey: PublicKey, commitment: Optional[commitment.Commitment] = commitment.Confirmed
    ) -> float:
        return float(self.client.get_token_account_balance(pubkey, commitment)["result"]["value"]["uiAmount"])

    def _terminate_localnet(self, timeout=10) -> None:
        """
        Borrowed from https://github.com/pytest-dev/pytest-xprocess/blob/6dac644e7b6b17d9b970f6e9e2bf2ade539841dc/xprocess/xprocess.py#L35.
        """
        parent = psutil.Process(self.localnet.pid)
        try:
            kill_list = [parent]
            kill_list += parent.children(recursive=True)

            # Attempt graceful termination first.
            for p in reversed(kill_list):
                self._signal_process(p, signal.SIGTERM)
            _, alive = psutil.wait_procs(kill_list, timeout=timeout)

            # Forcefully terminate procs still running.
            for p in alive:
                self._signal_process(p, signal.SIGKILL)
            _, alive = psutil.wait_procs(kill_list, timeout=timeout)

            if alive:
                raise Exception(f"could not terminated process {alive}")
        except (psutil.Error, ValueError) as err:
            raise Exception(f"Error while terminating process {err}")
        else:
            return

    def _signal_process(self, p, sig):
        """
        Borrowed from: https://github.com/pytest-dev/pytest-xprocess/blob/6dac644e7b6b17d9b970f6e9e2bf2ade539841dc/xprocess/xprocess.py#L29.
        """
        try:
            p.send_signal(sig)
        except psutil.NoSuchProcess:
            pass
