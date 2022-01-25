# solsim

<div align="center">
    <img src="https://raw.githubusercontent.com/cavaunpeu/solsim/add-readme/logo.png" width="70%" height="70%">
</div>

---

[![Discord Chat](https://img.shields.io/discord/889577356681945098?color=blueviolet)](https://discord.gg/sxy4zxBckh)

solsim is the Solana complex systems simulator. It simulates behavior of dynamical systems—e.g. DeFi protocols, DAO governance, cryptocurrencies—built on the [Solana](https://solana.com/) blockchain.

## Philosophy

Define your system how you see fit.

solsim will simulate its behavior and its collect results in a straightforward, structured manner.

## Usage

1. Implement `initialStep` and `step` methods how you see fit.
2. From each, return a dictionary mapping variables to current values.
3. Specify the variables you'd like to "watch."
4. Instantiate a `Simulation`, call `.run()`.
5. Receive a [pandas](https://pandas.pydata.org/) DataFrame of results.

## Installation

```sh
pip install solsim
```

### Development setup

First, install [poetry](https://python-poetry.org/).

Then:

```sh
git clone https://github.com/cavaunpeu/solsim.git
cd solsim
poetry install
poetry shell
```

## Detailed usage

### Systems using Solana

First, write the Solana programs in Rust or [Anchor](https://project-serum.github.io/anchor/getting-started/introduction.html) that comprise your system.

Next, copy the generated idl.json for each into a directory (e.g. named `workspace`) built as such:

```
workspace
└── target
    └── idl
        ├── program1.json
        ├── program2.json
        └── program3.json
```

Then,

1. Build a system class that inherits from `BaseSolanaSystem`.
2. Implement `initialStep` and `step` methods.
3. Call `super().__init__("workspace")` in its `__init__`.

In `3`, solsim exposes the following attributes to your system:

- `self.workspace`: IDL clients for the Solana programs that comprise your system (via [anchorpy](https://github.com/kevinheavey)).

For example, these clients let you interact with your respective programs' RPC endpoints.

- `self.client`: a general Solana client (via [solana-py](https://github.com/michaelhly/solana-py)).

This client lets you interact with Solana's RPC endpoints. Documentation [here](https://michaelhly.github.io/solana-py/api.html#).

Finally,

1. Define a `watchlist`: variables (returned in `initialStep` and `step`) you'd like to "watch."
2. Instantiate and run your simulation, e.g. `Simulation(MySystem(), watchlist, n_steps=10).run()`.

#### Example

See the [drunken escrow](https://github.com/cavaunpeu/solsim/tree/main/examples/drunken_escrow) system.

### Systems not using Solana

1. Build a system class that inherits from `BaseSystem`.
2. Implement `initialStep` and `step` methods.
3. Define a `watchlist`: variables (returned in `initialStep` and `step`) you'd like to "watch."
4. Instantiate and run your simulation, e.g. `Simulation(MySystem(), watchlist, n_steps=10).run()`.

#### Example

See the [Lotka-Volterra](https://github.com/cavaunpeu/solsim/tree/main/examples/drunken_escrow) system, inspired by [cadCAD Edu](https://www.cadcad.education/).