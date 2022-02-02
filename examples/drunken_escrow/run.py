import os

from .system import DrunkenEscrowSystem
from solsim.simulation import Simulation


def main(num_escrows=3, steps_per_run=4):
    simulation = Simulation(
        system=DrunkenEscrowSystem(
            workspace_dir=os.path.join(os.path.dirname(__file__), "anchor-escrow-program"),
            init_assoc_token_acct_balance=100,
            num_escrows=num_escrows,
        ),
        watchlist=("num_swaps", "mean_swap_amount", "mean_balance_spread"),
    )
    return simulation.run(steps_per_run=steps_per_run)


if __name__ == "__main__":
    main()
