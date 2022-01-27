import random
from typing import Dict, Tuple


from anchorpy import Context
import numpy as np
from solana.keypair import Keypair
from solana.publickey import PublicKey
from spl.token.instructions import get_associated_token_address

from solsim.system import BaseSolanaSystem
from solsim.constant import (
    SYSVAR_RENT_PUBKEY,
    TOKEN_PROGRAM_ID,
    SYS_PROGRAM_ID,
    ASSOCIATED_TOKEN_PROGRAM_ID,
)


class SimpleEscrow:
    def __init__(
        self,
        maker,
        taker,
        payer,
        foo_coin_mint,
        bar_coin_mint,
        foo_coin_mint_bump,
        bar_coin_mint_bump,
        program,
        init_assoc_token_acct_balance,
    ):
        self.maker = maker
        self.taker = taker
        self.payer = payer
        self.foo_coin_mint = foo_coin_mint
        self.bar_coin_mint = bar_coin_mint
        self.foo_coin_mint_bump = foo_coin_mint_bump
        self.bar_coin_mint_bump = bar_coin_mint_bump
        self.program = program
        self.init_assoc_token_acct_balance = init_assoc_token_acct_balance
        self.swap_state = Keypair()
        self.escrow_account, self.escrow_account_bump = PublicKey.find_program_address(
            [bytes(self.swap_state.public_key)], self.program.program_id
        )

    async def get_assoc_token_accounts(self):
        self.assoc_token_accts = {
            "maker": {
                "foo": get_associated_token_address(self.maker.public_key, self.foo_coin_mint),
                "bar": get_associated_token_address(self.maker.public_key, self.bar_coin_mint),
            },
            "taker": {
                "foo": get_associated_token_address(self.taker.public_key, self.foo_coin_mint),
                "bar": get_associated_token_address(self.taker.public_key, self.bar_coin_mint),
            },
        }

    async def init_maker_assoc_token_accounts(self):
        await self.program.rpc["init_maker_assoc_token_accts"](
            ctx=Context(
                accounts={
                    "foo_coin_mint": self.foo_coin_mint,
                    "bar_coin_mint": self.bar_coin_mint,
                    "maker_foo_coin_assoc_token_acct": self.assoc_token_accts["maker"]["foo"],
                    "maker_bar_coin_assoc_token_acct": self.assoc_token_accts["maker"]["bar"],
                    "payer": self.payer,
                    "maker": self.maker.public_key,
                    "token_program": TOKEN_PROGRAM_ID,
                    "associated_token_program": ASSOCIATED_TOKEN_PROGRAM_ID,
                    "rent": SYSVAR_RENT_PUBKEY,
                    "system_program": SYS_PROGRAM_ID,
                },
                signers=[self.maker],
            )
        )

    async def init_taker_assoc_token_accounts(self):
        await self.program.rpc["init_taker_assoc_token_accts"](
            ctx=Context(
                accounts={
                    "foo_coin_mint": self.foo_coin_mint,
                    "bar_coin_mint": self.bar_coin_mint,
                    "taker_foo_coin_assoc_token_acct": self.assoc_token_accts["taker"]["foo"],
                    "taker_bar_coin_assoc_token_acct": self.assoc_token_accts["taker"]["bar"],
                    "payer": self.payer,
                    "taker": self.taker.public_key,
                    "token_program": TOKEN_PROGRAM_ID,
                    "associated_token_program": ASSOCIATED_TOKEN_PROGRAM_ID,
                    "rent": SYSVAR_RENT_PUBKEY,
                    "system_program": SYS_PROGRAM_ID,
                },
                signers=[self.taker],
            )
        )

    async def initialize(self):
        await self.program.rpc["init_escrow"](
            self.escrow_account_bump,
            ctx=Context(
                accounts={
                    "foo_coin_mint": self.foo_coin_mint,
                    "swap_state": self.swap_state.public_key,
                    "escrow_account": self.escrow_account,
                    "payer": self.payer,
                    "token_program": TOKEN_PROGRAM_ID,
                    "rent": SYSVAR_RENT_PUBKEY,
                    "system_program": SYS_PROGRAM_ID,
                },
                signers=[self.swap_state],
            ),
        )

    async def reset_assoc_token_acct_balances(self):
        await self.program.rpc["reset_assoc_token_acct_balances"](
            self.foo_coin_mint_bump,
            self.bar_coin_mint_bump,
            self.init_assoc_token_acct_balance,
            ctx=Context(
                accounts={
                    "foo_coin_mint": self.foo_coin_mint,
                    "bar_coin_mint": self.bar_coin_mint,
                    "maker_foo_coin_assoc_token_acct": self.assoc_token_accts["maker"]["foo"],
                    "taker_bar_coin_assoc_token_acct": self.assoc_token_accts["taker"]["bar"],
                    "payer": self.payer,
                    "maker": self.maker.public_key,
                    "taker": self.taker.public_key,
                    "token_program": TOKEN_PROGRAM_ID,
                    "rent": SYSVAR_RENT_PUBKEY,
                    "system_program": SYS_PROGRAM_ID,
                },
                signers=[self.maker, self.taker],
            ),
        )

    async def submit(self, foo_coin_amount, bar_coin_amount):
        await self.program.rpc["submit"](
            self.escrow_account_bump,
            foo_coin_amount,
            bar_coin_amount,
            ctx=Context(
                accounts={
                    "bar_coin_mint": self.bar_coin_mint,
                    "swap_state": self.swap_state.public_key,
                    "maker_foo_coin_assoc_token_acct": self.assoc_token_accts["maker"]["foo"],
                    "escrow_account": self.escrow_account,
                    "payer": self.payer,
                    "maker": self.maker.public_key,
                    "token_program": TOKEN_PROGRAM_ID,
                    "rent": SYSVAR_RENT_PUBKEY,
                    "system_program": SYS_PROGRAM_ID,
                },
                signers=[self.maker],
            ),
        )

    async def accept(self):
        await self.program.rpc["accept"](
            ctx=Context(
                accounts={
                    "swap_state": self.swap_state.public_key,
                    "taker_bar_coin_assoc_token_acct": self.assoc_token_accts["taker"]["bar"],
                    "maker_bar_coin_assoc_token_acct": self.assoc_token_accts["maker"]["bar"],
                    "escrow_account": self.escrow_account,
                    "taker_foo_coin_assoc_token_acct": self.assoc_token_accts["taker"]["foo"],
                    "payer": self.payer,
                    "maker": self.maker.public_key,
                    "taker": self.taker.public_key,
                    "token_program": TOKEN_PROGRAM_ID,
                },
                signers=[self.taker],
            )
        )


class DrunkenEscrowSystem(BaseSolanaSystem):
    def __init__(self, workspace_dir: str, init_assoc_token_acct_balance: int, n_escrows: int):
        super().__init__(workspace_dir)
        self._escrow_program = self.workspace["anchor_escrow_program"]
        self.payer = self._escrow_program.provider.wallet.public_key
        self.init_assoc_token_acct_balance = init_assoc_token_acct_balance
        self.agents = [Keypair() for _ in range(n_escrows * 2)]

    def _compose_maker_taker_pairs(self):
        agents = list(self.agents)
        random.shuffle(agents)
        return [tuple(agents[i : i + 2]) for i in range(0, len(agents), 2)]  # noqa: E203

    async def _compose_escrows(self, step):
        pairs = self._compose_maker_taker_pairs()
        escrows = []
        for maker, taker in pairs:
            escrow = SimpleEscrow(
                maker,
                taker,
                self.payer,
                self.foo_coin_mint,
                self.bar_coin_mint,
                self.foo_coin_mint_bump,
                self.bar_coin_mint_bump,
                self._escrow_program,
                self.init_assoc_token_acct_balance,
            )
            await escrow.get_assoc_token_accounts()
            if step == -1:
                await escrow.init_maker_assoc_token_accounts()
                await escrow.init_taker_assoc_token_accounts()
                await escrow.reset_assoc_token_acct_balances()
            await escrow.initialize()
            escrows.append(escrow)
        return escrows

    async def _init_mints(self):
        self.foo_coin_mint, self.foo_coin_mint_bump = PublicKey.find_program_address(
            [bytes("foo", encoding="utf8")], self._escrow_program.program_id
        )
        self.bar_coin_mint, self.bar_coin_mint_bump = PublicKey.find_program_address(
            [bytes("bar", encoding="utf8")], self._escrow_program.program_id
        )
        await self._escrow_program.rpc["init_mints"](
            self.foo_coin_mint_bump,
            self.bar_coin_mint_bump,
            ctx=Context(
                accounts={
                    "foo_coin_mint": self.foo_coin_mint,
                    "bar_coin_mint": self.bar_coin_mint,
                    "payer": self.payer,
                    "token_program": TOKEN_PROGRAM_ID,
                    "rent": SYSVAR_RENT_PUBKEY,
                    "system_program": SYS_PROGRAM_ID,
                }
            ),
        )

    def _propose_escrow_terms(self, escrow) -> Tuple[float, float]:
        maker_foo_balance = self.get_token_account_balance(escrow.assoc_token_accts["maker"]["foo"])
        taker_bar_balance = self.get_token_account_balance(escrow.assoc_token_accts["taker"]["bar"])
        if maker_foo_balance > 1 and taker_bar_balance > 1:
            foo_amt = np.random.randint(1, maker_foo_balance)
            bar_amt = np.random.randint(1, taker_bar_balance)
            amt = min(foo_amt, bar_amt)
            terms = (amt, amt)
        else:
            terms = (None, None)
        return terms

    async def _swap(self, step: int):
        escrows = await self._compose_escrows(step)
        amounts = []
        for escrow in escrows:
            terms = self._propose_escrow_terms(escrow)
            if terms != (None, None):
                foo_coin_amount, bar_coin_amount = terms
                await escrow.submit(foo_coin_amount, bar_coin_amount)
                await escrow.accept()
                amounts.append(foo_coin_amount)  # foo_coin_amount and bar_coin_amount always equivalent
        return escrows, amounts

    def _compute_balance_spread_stats(self, escrows):
        spreads = []
        for escrow in escrows:
            for role in ["maker", "taker"]:
                spread = abs(
                    self.get_token_account_balance(escrow.assoc_token_accts[role]["foo"])
                    - self.get_token_account_balance(escrow.assoc_token_accts[role]["bar"])  # noqa: W503
                )
                spreads.append(spread)
        return {"mean_balance_spread": np.mean(spreads)}

    def _compute_swap_amount_stats(self, amounts):
        return {"num_swaps": len(amounts), "mean_swap_amount": np.mean(amounts)}

    async def initialStep(self) -> Dict:
        await self._init_mints()
        escrows, amounts = await self._swap(step=-1)
        return {
            **self._compute_swap_amount_stats(amounts),
            **self._compute_balance_spread_stats(escrows),
        }

    async def step(self, state, history) -> Dict:
        escrows, amounts = await self._swap(step=len(history) - 1)
        return {
            **self._compute_swap_amount_stats(amounts),
            **self._compute_balance_spread_stats(escrows),
        }
