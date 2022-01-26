import os

from .system import SimpleEscrowSystem
from solsim.simulation import Simulation


def main():
    simulation = Simulation(
        system=SimpleEscrowSystem(
            workspace_dir=os.path.expanduser('~/code/crypto/anchor-escrow-program'),
            init_assoc_token_acct_balance=100,
            num_escrows=3,
        ),
        watchlist=("num_swaps", "mean_swap_amount", "mean_balance_spread"),
        n_steps=3,
    )
    results = simulation.run()


if __name__ == "__main__":
    main()
