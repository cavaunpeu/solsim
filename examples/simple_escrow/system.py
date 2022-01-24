import os
from typing import Dict

from anchorpy import create_workspace, close_workspace, Context
from solana.keypair import Keypair
from solana.publickey import PublicKey
from spl.token.instructions import get_associated_token_address

from solsim.base import BaseSolanaSystem
from solsim.constants import (
  SYSVAR_RENT_PUBKEY,
  TOKEN_PROGRAM_ID,
  SYS_PROGRAM_ID,
  ASSOCIATED_TOKEN_PROGRAM_ID
)


class SimpleEscrowSystem(BaseSolanaSystem):

  def __init__(
    self,
    workspace_dir: str,
    init_assoc_token_acct_balance: int
  ):
    super().__init__(workspace_dir)
    self._escrow_program = self.workspace['simple_escrow']
    self._init_addresses()
    self.payer = self._escrow_program.provider.wallet.public_key
    self.init_assoc_token_acct_balance = init_assoc_token_acct_balance

  def _init_addresses(self):
    self.foo_coin_mint, self.foo_coin_mint_bump = PublicKey.find_program_address([bytes("foo", encoding='utf8')], self._escrow_program.program_id)
    self.bar_coin_mint, self.bar_coin_mint_bump = PublicKey.find_program_address([bytes("bar", encoding='utf8')], self._escrow_program.program_id)
    self.maker = Keypair()
    self.taker = Keypair()
    self.swap_state = Keypair()
    self.escrow_account, self.escrow_account_bump = PublicKey.find_program_address([bytes(self.swap_state.public_key)], self._escrow_program.program_id)

  async def _initialize_escrow(self):
    await self._init_mints()
    await self._init_associated_token_accounts()
    await self._init_maker_assoc_token_accounts()
    await self._init_taker_assoc_token_accounts()
    await self._init_escrow()

  async def _init_mints(self):
    await self._escrow_program.rpc['init_mints'](
      self.foo_coin_mint_bump,
      self.bar_coin_mint_bump,
      ctx=Context(
        accounts={
          'foo_coin_mint': self.foo_coin_mint,
          'bar_coin_mint': self.bar_coin_mint,
          'payer': self.payer,
          'token_program': TOKEN_PROGRAM_ID,
          'rent': SYSVAR_RENT_PUBKEY,
          'system_program': SYS_PROGRAM_ID
        }
      )
    )

  async def _init_associated_token_accounts(self):
    self.maker_foo_coin_assoc_token_acct = get_associated_token_address(self.maker.public_key, self.foo_coin_mint)
    self.maker_bar_coin_assoc_token_acct = get_associated_token_address(self.maker.public_key, self.bar_coin_mint)
    self.taker_foo_coin_assoc_token_acct = get_associated_token_address(self.taker.public_key, self.foo_coin_mint)
    self.taker_bar_coin_assoc_token_acct = get_associated_token_address(self.taker.public_key, self.bar_coin_mint)

  async def _init_maker_assoc_token_accounts(self):
    await self._escrow_program.rpc['init_maker_assoc_token_accts'](
      ctx=Context(
        accounts={
          'foo_coin_mint': self.foo_coin_mint,
          'bar_coin_mint': self.bar_coin_mint,
          'maker_foo_coin_assoc_token_acct': self.maker_foo_coin_assoc_token_acct,
          'maker_bar_coin_assoc_token_acct': self.maker_bar_coin_assoc_token_acct,
          'payer': self.payer,
          'maker': self.maker.public_key,
          'token_program': TOKEN_PROGRAM_ID,
          'associated_token_program': ASSOCIATED_TOKEN_PROGRAM_ID,
          'rent': SYSVAR_RENT_PUBKEY,
          'system_program': SYS_PROGRAM_ID
        },
        signers=[self.maker]
      )
    )

  async def _init_taker_assoc_token_accounts(self):
    await self._escrow_program.rpc['init_taker_assoc_token_accts'](
      ctx=Context(
        accounts={
          'foo_coin_mint': self.foo_coin_mint,
          'bar_coin_mint': self.bar_coin_mint,
          'taker_foo_coin_assoc_token_acct': self.taker_foo_coin_assoc_token_acct,
          'taker_bar_coin_assoc_token_acct': self.taker_bar_coin_assoc_token_acct,
          'payer': self.payer,
          'taker': self.taker.public_key,
          'token_program': TOKEN_PROGRAM_ID,
          'associated_token_program': ASSOCIATED_TOKEN_PROGRAM_ID,
          'rent': SYSVAR_RENT_PUBKEY,
          'system_program': SYS_PROGRAM_ID
        },
        signers=[self.taker]
      )
    )

  async def _init_escrow(self):
    await self._escrow_program.rpc['init_escrow'](
      self.escrow_account_bump,
      ctx=Context(
        accounts={
          'foo_coin_mint': self.foo_coin_mint,
          'swap_state': self.swap_state.public_key,
          'escrow_account': self.escrow_account,
          'payer': self.payer,
          'token_program': TOKEN_PROGRAM_ID,
          'rent': SYSVAR_RENT_PUBKEY,
          'system_program': SYS_PROGRAM_ID
        },
        signers=[self.swap_state]
      )
    )

  async def _reset_assoc_token_acct_balances(self):
    await self._escrow_program.rpc['reset_assoc_token_acct_balances'](
      self.foo_coin_mint_bump,
      self.bar_coin_mint_bump,
      self.init_assoc_token_acct_balance,
      ctx=Context(
        accounts={
          'foo_coin_mint': self.foo_coin_mint,
          'bar_coin_mint': self.bar_coin_mint,
          'maker_foo_coin_assoc_token_acct': self.maker_foo_coin_assoc_token_acct,
          'taker_bar_coin_assoc_token_acct': self.taker_bar_coin_assoc_token_acct,
          'payer': self.payer,
          'maker': self.maker.public_key,
          'taker': self.taker.public_key,
          'token_program': TOKEN_PROGRAM_ID,
          'rent': SYSVAR_RENT_PUBKEY,
          'system_program': SYS_PROGRAM_ID
        },
        signers=[self.maker, self.taker]
      )
    )

  async def _submit(self, foo_coin_amount, bar_coin_amount):
    await self._escrow_program.rpc['submit'](
      self.escrow_account_bump,
      foo_coin_amount,
      bar_coin_amount,
      ctx=Context(
        accounts={
          'bar_coin_mint': self.bar_coin_mint,
          'swap_state': self.swap_state.public_key,
          'maker_foo_coin_assoc_token_acct': self.maker_foo_coin_assoc_token_acct,
          'escrow_account': self.escrow_account,
          'payer': self.payer,
          'maker': self.maker.public_key,
          'token_program': TOKEN_PROGRAM_ID,
          'rent': SYSVAR_RENT_PUBKEY,
          'system_program': SYS_PROGRAM_ID
        },
        signers=[self.maker]
      )
    )

  async def initialStep(self) -> Dict:
    await self._initialize_escrow()
    await self._reset_assoc_token_acct_balances()
    await self._submit(foo_coin_amount=10, bar_coin_amount=20)
    return {
      'foo_coin_trade_volume': 1,
      'bar_coin_trade_volume': 1,
    }

  async def step(self, state, history) -> Dict:
    return {
      'foo_coin_trade_volume': 1,
      'bar_coin_trade_volume': 1,
    }