from abc import ABC, abstractmethod
import time
import psutil
import signal
import subprocess
from subprocess import DEVNULL
import tempfile
from typing import Awaitable, Optional, List, Any

from anchorpy import close_workspace, create_workspace
from psutil import Process
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc import commitment

from solsim.type import StateType


class BaseMixin:
    @property
    def uses_solana(self) -> bool:
        return isinstance(self, BaseSolanaSystem)

    def setup(self) -> Any:
        pass

    def teardown(self) -> Any:
        pass

    def cleanup(self) -> Any:
        pass


class BaseSystem(ABC, BaseMixin):
    @abstractmethod
    def initial_step(self) -> StateType:
        """Return initial system state.

        Returns:
            The initial state of the system.
        """
        raise NotImplementedError

    @abstractmethod
    def step(self, state: StateType, history: List[StateType]) -> StateType:
        """Return an arbitrary state of the system.

        This method is `async` because it (presumably) will make RPC calls
        to the Solana blockchain, which are `async`.

        Args:
            state: The previous system state.
            history: The full history of system states.

        Returns:
            The initial state of the system.
        """
        raise NotImplementedError


class BaseSolanaSystem(ABC, BaseMixin):

    SOLANA_CLUSTER_URI = "http://127.0.0.1:8899"

    def __init__(
        self, workspace_dir: str, client: Optional[Client] = None, localnet_process: Optional[Process] = None
    ) -> None:
        self._workspace_dir = workspace_dir
        self._localnet_process = localnet_process
        self._localnet_initialized = False
        self.setup()
        self.client = client or Client(self.SOLANA_CLUSTER_URI)
        self.workspace = create_workspace(self._workspace_dir)

    def setup(self) -> None:
        if not self._localnet_initialized:
            if not self._localnet_process:
                self._logfile = tempfile.NamedTemporaryFile()
                self._localnet = self._start_localnet()
                print("👆 Starting Solana localnet cluster (~5s) ...")
                while not self._localnet_ready:
                    time.sleep(1)
            else:
                self._localnet = self._localnet_process
            self._localnet_initialized = True

    def teardown(self) -> None:
        if self._localnet_initialized:
            print("👇 Terminating Solana localnet cluster ...")
            self._terminate_localnet()
        self._localnet_initialized = False

    async def cleanup(self) -> None:
        await close_workspace(self.workspace)

    @abstractmethod
    async def initial_step(self) -> Awaitable[StateType]:
        """Return initial system state.

        This method is `async` because it (presumably) will make RPC calls
        to the Solana blockchain, which are `async`.

        Returns:
            The initial state of the system.
        """
        raise NotImplementedError

    @abstractmethod
    async def step(self, state: StateType, history: List[StateType]) -> Awaitable[StateType]:
        """Return an arbitrary state of the system.

        This method is `async` because it (presumably) will make RPC calls
        to the Solana blockchain, which are `async`.

        Args:
            state: The previous system state.
            history: The full history of system states.

        Returns:
            The initial state of the system.
        """
        raise NotImplementedError

    def _start_localnet(self) -> subprocess.Popen[Any]:
        for proc in psutil.process_iter():
            if proc.name() == "solana-test-validator":
                self._terminate_processes([proc])
        return subprocess.Popen(["anchor", "localnet"], cwd=self._workspace_dir, stdout=self._logfile, stderr=DEVNULL)

    @property
    def _localnet_ready(self) -> bool:
        lastline = subprocess.check_output(["tail", "-n", "1", self._logfile.name]).decode("utf-8").strip()
        return "| Processed Slot: " in lastline

    def get_token_account_balance(
        self, pubkey: PublicKey, commitment: Optional[commitment.Commitment] = commitment.Confirmed
    ) -> float:
        """Get account token balance.

        Args:
            pubkey: The public key of the account in question.

        Returns:
            The token balance of the account.
        """
        return float(self.client.get_token_account_balance(pubkey, commitment)["result"]["value"]["uiAmount"])

    def _terminate_processes(self, kill_list: list[Process], timeout: int = 10) -> None:
        # Attempt graceful termination first.
        for p in reversed(kill_list):
            self._signal_process(p, signal.SIGTERM)
        _, alive = psutil.wait_procs(kill_list, timeout=timeout)

        # Forcefully terminate procs still running.
        for p in alive:
            self._signal_process(p, signal.SIGKILL)
        _, alive = psutil.wait_procs(kill_list, timeout=timeout)

        if alive:
            raise Exception(f"could not terminate process {alive}")

    def _terminate_localnet(self) -> None:
        """
        Borrowed from https://github.com/pytest-dev/pytest-xprocess/blob/6dac644e7b6b17d9b970f6e9e2bf2ade539841dc/xprocess/xprocess.py#L35.  # noqa E501
        """
        parent = psutil.Process(self._localnet.pid)
        try:
            kill_list = [parent]
            kill_list += parent.children(recursive=True)
            self._terminate_processes(kill_list)
        except (psutil.Error, ValueError) as err:
            raise Exception(f"Error while terminating process {err}")
        else:
            return

    def _signal_process(self, p: Process, sig: signal.Signals) -> None:
        """
        Borrowed from: https://github.com/pytest-dev/pytest-xprocess/blob/6dac644e7b6b17d9b970f6e9e2bf2ade539841dc/xprocess/xprocess.py#L29.  # noqa E501
        """
        try:
            p.send_signal(sig)
        except psutil.NoSuchProcess:
            pass
