import os

from .system import DrunkenEscrowSystem
from solsim.simulation import Simulation


def main(n_escrows=3, n_steps=4):
    simulation = Simulation(
        system=DrunkenEscrowSystem(
            workspace_dir=os.path.join(os.path.dirname(__file__), "anchor-escrow-program"),
            init_assoc_token_acct_balance=100,
            n_escrows=n_escrows,
        ),
        watchlist=("num_swaps", "mean_swap_amount", "mean_balance_spread"),
        n_steps=n_steps,
    )
    return simulation.run()


if __name__ == "__main__":
    main()
