import os

from .system import DrunkenEscrowSystem
from solsim.simulation import Simulation


def main(num_escrows=3, num_steps=4):
    simulation = Simulation(
        system=DrunkenEscrowSystem(
            workspace_dir=os.path.join(os.path.dirname(__file__), "anchor-escrow-program"),
            init_assoc_token_acct_balance=100,
            num_escrows=num_escrows,
        ),
        watchlist=("num_swaps", "mean_swap_amount", "mean_balance_spread")
    )
    return simulation.run(num_steps_per_run=num_steps)


if __name__ == "__main__":
    main()
