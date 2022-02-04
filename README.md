# solsim

<div align="center">
    <img src="https://raw.githubusercontent.com/cavaunpeu/solsim/main/img/logo.png" width="70%" height="70%">
</div>

---

<!-- Badges -->

[![Discord Chat](https://img.shields.io/discord/889577356681945098?color=blueviolet)](https://discord.gg/sxy4zxBckh)
[![Downloads](https://pepy.tech/badge/solsim)](https://pepy.tech/project/solsim)

<!-- Tests and Lint Badges -->

<div>
<img alt="Tests" src="https://github.com/cavaunpeu/solsim/actions/workflows/tests.yml/badge.svg">
<img alt="Lint" src="https://github.com/cavaunpeu/solsim/actions/workflows/lint.yml/badge.svg">
</div>

---

## Introduction

solsim is the Solana complex systems simulator. It simulates behavior of dynamical systems—DeFi protocols, DAO governance, cryptocurrencies, and more—built on the [Solana](https://solana.com/) blockchain.

## Philosophy

Define your system how you see fit.

solsim will simulate its behavior and collect its results in a structured, straightforward manner.

## Usage

1. Implement `initial_step` and `step` methods.
2. From each, return the current state, i.e. a dictionary mapping variables to current values.
3. Specify the variables you'd like to "watch."
4. Instantiate a Simulation, call `.run()`.
5. Receive a [pandas](https://pandas.pydata.org/) DataFrame containing values of "watched" variables at each step in time.

### With Solana

```python
from anchorpy import Context
from solana.keypair import Keypair
from solsim.simulation import Simulation

class SomeSolanaSystem(BaseSolanaSystem):
    def __init__(self):
        super().__init__("path/to/workspace")
        self.account = Keypair()
        self.pubkey = self.account.public_key
        self.program = self.workspace["my_anchor_program"]  # solsim gives a Anchor program workspace (self.workspace).

    async def initial_step(self):
        self.program.rpc["initialize"]()  # Make RPC calls to your Anchor program.
        await self.client.request_airdrop(self.pubkey, 10)  # solsim gives you a Solana API client (self.client).
        return {"balance": await self.client.get_balance(self.pubkey)}

    async def step(self, state, history):
        self.program.rpc["submit_uniswap_trade"](
            ctx=Context(accounts={"account": self.pubkey}, signers=[self.account])
        )
        return {"balance": await self.client.get_balance(self.account)}


simulation = Simulation(system=SomeSolanaSystem(), watchlist=("balance"))
results = simulation.run(steps_per_run=5)  # Returns pandas DataFrame of results.
```

### Without Solana

```python
class SomeSystem(BaseSystem):
    def __init__(self, population):
        self.pop = population

    def initial_step(self):
        return {"population": self.pop}

    def step(self, state, history):
        return {"population": state["population"] * 1.1}


simulation = Simulation(system=SomeSystem(), watchlist=("population"))
results = simulation.run(steps_per_run=5)
```

## CLI

Optionally run your simulations via CLI. Instead of calling `simulation.run()` in your code:

1. Call `simulation.cli()`.
2. Run your simulation as e.g. `python path/to/file.py run --num-runs 3`.

## Results Explorer

solsim gives you a streamlit app to explore results, e.g.

<div>
    <img src="https://raw.githubusercontent.com/cavaunpeu/solsim/main/img/results_explorer_app.png">
</div>

To automatically start this app following simulation, invoke one of the following:

- `simulation.run(visualize_results=True)`
- `--viz-results` flag in the CLI runner, e.g. `python path/to/file.py run --viz-results`

## Installation

First, install [Anchor](https://project-serum.github.io/anchor/getting-started/installation.html#install-rust).

### Library

```sh
pip install solsim
```

### Development

Install [poetry](https://python-poetry.org/). Then,

```sh
git clone --recurse-submodules https://github.com/cavaunpeu/solsim.git
cd solsim
poetry install
poetry shell
```

## Detailed Usage

### With Solana

First, write your Solana program. solsim prefers you do this in [Anchor](https://project-serum.github.io/anchor/getting-started/introduction.html). Then,

1. Write a system class that inherits from `BaseSolanaSystem`.
2. Call `super().__init__("path/to/program")` in its `__init__`.
3. Implement `initial_step` and `step` methods. (Since you'll interact with Solana asynchronously, these methods should be `async`.)

In `2.`, solsim exposes the following attributes to your system instance:

- `self.workspace`: IDL clients for the Solana programs that comprise your system (via [anchorpy](https://github.com/kevinheavey/anchorpy)).

For example, these clients let you interact with your respective programs' RPC endpoints.

- `self.client`: a general Solana client (via [solana-py](https://github.com/michaelhly/solana-py)).

This client lets you interact with Solana's RPC endpoints. Documentation [here](https://michaelhly.github.io/solana-py/api.html#).

Finally,

1. Define a `watchlist`: variables (returned in `initial_step` and `step`) you'd like to "watch."
2. Instantiate and run your simulation, e.g. `Simulation(MySystem(), watchlist).run(steps_per_run=10)`.

### Without Solana

1. Write a system class that inherits from `BaseSystem`.
2. Implement `initial_step` and `step` methods.
3. Define a `watchlist`.
4. Instantiate and run your simulation.

## Examples

### Drunken Escrow

Agents are randomly paired to exchange random amounts of `foo_coin` and `bar_coin` via an Anchor escrow contract in each timestep.

- Run: `python -m examples.drunken_escrow`.
- Code: [here](https://github.com/cavaunpeu/solsim/tree/main/examples/drunken_escrow).
- Expected output (numbers may vary):

```
(.venv) ➜  solsim git:(main) python -m examples.drunken_escrow
👆 Starting Solana localnet cluster (~5s) ...
🟢 run: 0 | step: 100%|███████████████████████████████████████████████████████████████████████████████████| 4/4 [00:34<00:00,  8.60s/it]
👇 Terminating Solana localnet cluster ...
   step  run  mean_balance_spread  mean_swap_amount  num_swaps
0     0    0            17.333333         41.333333          3
1     1    0            22.000000          4.666667          3
2     2    0            40.000000         25.666667          3
3     3    0            44.000000         14.666667          3
```

### Lotka-Volterra

The Lotka-Volterra model is a classic dynamical system in the field of ecology that tracks the evolution of interdependent predator and prey populations.

- Run: `python -m examples.lotka_volterra`.
- Code: [here](https://github.com/cavaunpeu/solsim/tree/main/examples/lotka_volterra).
- Expected output:

```
(.venv) ➜  solsim git:(main) python -m examples.lotka_volterra
🟢 run: 0 | step: 100%|████████████████████████████████████████████████████████████████████████████████| 4/4 [00:00<00:00, 70492.50it/s]
   step  run  food_supply  population_size
0     0    0     1000.000            50.00
1     1    0      995.000            60.00
2     2    0      989.000            69.95
3     3    0      982.005            79.84
```

This example is inspired by [cadCAD Edu](https://www.cadcad.education/).

## Inspiration

solsim humbly builds on the shoulders of the giants that are [cadCAD](https://github.com/cadCAD-org/cadCAD) and [tokenspice](https://github.com/tokenspice/tokenspice), among others.