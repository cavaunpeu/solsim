from .system import LotkaVolterraSystem
from solsim.simulation import Simulation


def main():
    simulation = Simulation(
        system=LotkaVolterraSystem(
            population_size=50,
            food_supply=1000,
            reproduction_rate=0.01,
            consumption_rate=0.1,
        ),
        watchlist=("population_size", "food_supply")
    )
    return simulation.run(num_steps_per_run=4)


if __name__ == "__main__":
    main()
