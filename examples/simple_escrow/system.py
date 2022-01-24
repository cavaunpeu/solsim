import os
from typing import Dict

from anchorpy import create_workspace, close_workspace, Context
from solana.publickey import PublicKey

from solsim.base import BaseSolanaSystem
from solsim.constants import (
  SYSVAR_RENT_PUBKEY,
  TOKEN_PROGRAM_ID,
  SYS_PROGRAM_ID
)


class SimpleEscrowSystem(BaseSolanaSystem):

  def __init__(
    self,
    workspace_dir: str = 'workspace'
  ):
    super().__init__(workspace_dir)
    self._escrow_program = self.workspace['simple_escrow']
    self._init_addresses()
    self.payer = self._escrow_program.provider.wallet.public_key

  def _init_addresses(self):
    self.foo_coin_mint, self.foo_coin_mint_bump = PublicKey.find_program_address([bytes("foo", encoding='utf8')], self._escrow_program.program_id)
    self.bar_coin_mint, self.bar_coin_mint_bump = PublicKey.find_program_address([bytes("bar", encoding='utf8')], self._escrow_program.program_id)

  async def _initialize_escrow(self):
    await self._init_mints()

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

  async def initialStep(self) -> Dict:
    await self._initialize_escrow()
    return {
      'foo_coin_trade_volume': 1,
      'bar_coin_trade_volume': 1,
    }

  async def step(self, state, history) -> Dict:
    return {
      'foo_coin_trade_volume': 1,
      'bar_coin_trade_volume': 1,
    }