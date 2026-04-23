"""
AFX DEX Python SDK

Lightweight client for the AFX DEX API. Handles EIP-712 signing,
protobuf serialization, and HTTP requests.

Dependencies:
    pip install eth-account requests websockets

Usage:
    from dex_client import DexClient

    client = DexClient(
        master_key="0x...",
        agent_key="0x...",
        testnet=True,
    )
    client.faucet_claim()
    client.approve_agent()
    client.place_order(symbol_code=1, px="40000", qty="0.5", side="BUY")
"""

import asyncio
import json
import struct
import time
from typing import Optional

import requests
from eth_account import Account
from eth_hash.auto import keccak

# ═══════════════════════════════════════════════════════════════════
#  Config
# ═══════════════════════════════════════════════════════════════════

MAINNET = {
    "base_url": "https://api10.afx.xyz",
    "ws_url": "wss://ws10.afx.xyz/ws/dex",
    "chain_id": 42161,
    "source": "a",
    "dex_chain": "Mainnet",
}

TESTNET = {
    "base_url": "https://api10-testnet.afx.xyz",
    "ws_url": "wss://ws10-testnet.afx.xyz/ws/dex",
    "chain_id": 421614,
    "source": "b",
    "dex_chain": "Testnet",
}

EIP712_DOMAIN_TYPE = [
    {"name": "name", "type": "string"},
    {"name": "version", "type": "string"},
    {"name": "chainId", "type": "uint256"},
    {"name": "verifyingContract", "type": "address"},
]

ZERO_ADDR = "0x" + "0" * 40


# ═══════════════════════════════════════════════════════════════════
#  Protobuf Encoder (hand-rolled, no codegen needed)
# ═══════════════════════════════════════════════════════════════════

class Proto:
    """Minimal protobuf encoder for DEX messages."""

    @staticmethod
    def _varint(value):
        buf = bytearray()
        while value > 0x7F:
            buf.append((value & 0x7F) | 0x80)
            value >>= 7
        buf.append(value & 0x7F)
        return bytes(buf)

    @staticmethod
    def _signed_varint(value):
        """Encode a signed int64 as varint (two's complement for negatives)."""
        if value < 0:
            value = value + (1 << 64)
        return Proto._varint(value)

    @staticmethod
    def _field(field_num, wire_type, data):
        return Proto._varint((field_num << 3) | wire_type) + data

    @staticmethod
    def string(field_num, s):
        if not s:
            return b""
        encoded = s.encode("utf-8")
        return Proto._field(field_num, 2, Proto._varint(len(encoded)) + encoded)

    @staticmethod
    def int64(field_num, value):
        if value == 0:
            return b""
        return Proto._field(field_num, 0, Proto._signed_varint(value))

    @staticmethod
    def bool_(field_num, value):
        if not value:
            return b""
        return Proto._field(field_num, 0, Proto._varint(1))

    @staticmethod
    def enum(field_num, value):
        return Proto.int64(field_num, value)

    @staticmethod
    def embedded(field_num, data):
        return Proto._field(field_num, 2, Proto._varint(len(data)) + data)

    # ── Message builders ──

    @staticmethod
    def place_orders(orders):
        outer = b""
        for o in orders:
            inner = b""
            inner += Proto.int64(1, o.get("cl_ord_id", 0))
            inner += Proto.int64(2, o["symbol_code"])
            inner += Proto.string(3, o["ord_px"])
            inner += Proto.string(4, o["ord_qty"])
            inner += Proto.string(5, o.get("trigger_px", ""))
            inner += Proto.enum(6, o.get("ord_type", 0))
            inner += Proto.enum(7, o.get("ord_side", 0))
            inner += Proto.enum(8, o.get("time_in_force", 0))
            inner += Proto.enum(9, o.get("reduce_only_option", 0))
            inner += Proto.int64(10, o.get("parent_ord_id", 0))
            inner += Proto.enum(11, o.get("tpsl_trigger_type", 0))
            inner += Proto.string(12, o.get("slippage_pct", ""))
            outer += Proto.embedded(1, inner)
        return outer

    @staticmethod
    def cancel_orders(cancels):
        outer = b""
        for c in cancels:
            inner = b""
            inner += Proto.int64(1, c["symbol_code"])
            inner += Proto.int64(2, c.get("cl_ord_id", 0))
            inner += Proto.int64(3, c.get("ord_id", 0))
            outer += Proto.embedded(1, inner)
        return outer

    @staticmethod
    def cancel_all(symbol_code, is_conditional=False):
        return Proto.int64(1, symbol_code) + Proto.bool_(2, is_conditional)

    @staticmethod
    def set_leverage(symbol_code, leverage):
        return Proto.int64(1, symbol_code) + Proto.string(2, leverage)

    @staticmethod
    def set_margin_mode(symbol_code, margin_mode):
        return Proto.int64(1, symbol_code) + Proto.enum(2, margin_mode)

    @staticmethod
    def assign_pos_margin(symbol_code, amount):
        return Proto.int64(1, symbol_code) + Proto.string(2, amount)

    @staticmethod
    def vault_create(name, description, amount, currency_code):
        return (Proto.string(1, name) + Proto.string(2, description) +
                Proto.string(3, amount) + Proto.int64(4, currency_code))

    @staticmethod
    def vault_create_sub_vault():
        return b""

    @staticmethod
    def vault_deposit(amount, currency_code):
        return Proto.string(1, amount) + Proto.int64(2, currency_code)

    @staticmethod
    def vault_withdraw(amount, currency_code):
        return Proto.string(1, amount) + Proto.int64(2, currency_code)

    @staticmethod
    def vault_pre_withdraw(amount, currency_code):
        return Proto.string(1, amount) + Proto.int64(2, currency_code)

    @staticmethod
    def vault_rebalance(from_addr, to_addr, amount, currency_code):
        return (Proto.string(1, from_addr) + Proto.string(2, to_addr) +
                Proto.string(3, amount) + Proto.int64(4, currency_code))

    @staticmethod
    def vault_update_owner(owner):
        return Proto.string(1, owner)

    @staticmethod
    def vault_close():
        return b""

    @staticmethod
    def bind_referral(code):
        return Proto.string(1, code)


# ═══════════════════════════════════════════════════════════════════
#  Enum maps (string → int)
# ═══════════════════════════════════════════════════════════════════

ORD_TYPE = {"LIMIT": 1, "MARKET": 2}
ORD_SIDE = {"BUY": 1, "SELL": 2, "BUY_CLOSE_HEDGE": 3, "SELL_CLOSE_HEDGE": 4}
ORD_TIF = {"GTC": 1, "IOC": 2, "FOK": 3, "POST_ONLY": 4}
REDUCE_ONLY = {"REDUCE_ONLY": 1, "TP_FROM_POSITION": 2, "SL_FROM_POSITION": 3}
TRIGGER_TYPE = {"LAST_PRICE": 1, "MARK_PRICE": 2, "INDEX_PRICE": 3}
MARGIN_MODE = {"CROSS": 1, "ISOLATED": 2}


# ═══════════════════════════════════════════════════════════════════
#  DexClient
# ═══════════════════════════════════════════════════════════════════

class DexClient:
    """AFX DEX API client."""

    def __init__(self, master_key: str, agent_key: str, testnet: bool = True):
        env = TESTNET if testnet else MAINNET
        self.base_url = env["base_url"]
        self.ws_url = env["ws_url"]
        self.chain_id = env["chain_id"]
        self.source = env["source"]
        self.dex_chain = env["dex_chain"]

        self.master_key = master_key
        self.agent_key = agent_key
        self.master_addr = Account.from_key(master_key).address
        self.agent_addr = Account.from_key(agent_key).address

    # ── Low-level ────────────────────────────────────────────────

    def _sign_eip712(self, private_key, primary_type, type_fields, domain, message):
        signed = Account.sign_typed_data(private_key, full_message={
            "types": {"EIP712Domain": EIP712_DOMAIN_TYPE, primary_type: type_fields},
            "primaryType": primary_type,
            "domain": domain,
            "message": message,
        })
        return {
            "r": "0x" + format(signed.r, "064x"),
            "s": "0x" + format(signed.s, "064x"),
            "v": signed.v,
        }

    def _post(self, body):
        resp = requests.post(f"{self.base_url}/api/v1/exchange", json=body, timeout=15)
        return resp.json()

    def _get(self, path, params=None):
        resp = requests.get(f"{self.base_url}{path}", params=params or {}, timeout=15)
        return resp.json()

    # ── Agent signing ────────────────────────────────────────────

    def _agent_sign_and_send(self, action, proto_bytes,
                              vault_address=None, expiry_after=0):
        nonce = int(time.time() * 1000)
        parts = bytearray(proto_bytes)
        if vault_address:
            parts += bytes.fromhex(vault_address[2:])
        parts += struct.pack("<Q", nonce)
        parts += struct.pack("<Q", expiry_after)
        connection_id = keccak(bytes(parts))

        sig = self._sign_eip712(
            self.agent_key, "Agent",
            [{"name": "source", "type": "string"},
             {"name": "connectionId", "type": "bytes32"}],
            {"name": "Exchange", "version": "1",
             "chainId": self.chain_id, "verifyingContract": ZERO_ADDR},
            {"source": self.source,
             "connectionId": "0x" + connection_id.hex()},
        )
        return self._post({
            "action": action, "signature": sig, "nonce": nonce,
            "expiryAfter": expiry_after if expiry_after else None,
            "vaultAddress": vault_address,
        })

    # ── Master signing ───────────────────────────────────────────

    def _master_sign_and_send(self, action, primary_type, type_fields,
                               message, expiry_after=0):
        nonce = int(time.time() * 1000)
        sig = self._sign_eip712(
            self.master_key, primary_type, type_fields,
            {"name": "SignTransaction", "version": "1",
             "chainId": self.chain_id, "verifyingContract": ZERO_ADDR},
            message,
        )
        return self._post({
            "action": action, "signature": sig, "nonce": nonce,
            "expiryAfter": expiry_after if expiry_after else None,
        })

    # ═════════════════════════════════════════════════════════════
    #  Public API — Master signed
    # ═════════════════════════════════════════════════════════════

    def faucet_claim(self):
        """Claim testnet funds (testnet only)."""
        return self._master_sign_and_send(
            {"type": "faucetClaim"},
            "TestnetFaucetClaim",
            [{"name": "dexChain", "type": "string"}],
            {"dexChain": "Testnet"},
        )

    def approve_agent(self, agent_name="default", expiry_seconds=300):
        """Authorize the agent wallet."""
        nonce = int(time.time() * 1000)
        expiry_after = int(time.time()) + expiry_seconds
        return self._master_sign_and_send(
            {"type": "approveAgent", "agentAddress": self.agent_addr,
             "agentName": agent_name, "dexChain": self.dex_chain},
            "ApproveAgent",
            [{"name": "dexChain", "type": "string"},
             {"name": "agentAddress", "type": "address"},
             {"name": "agentName", "type": "string"},
             {"name": "nonce", "type": "uint64"},
             {"name": "expiryAfter", "type": "uint64"}],
            {"dexChain": self.dex_chain, "agentAddress": self.agent_addr,
             "agentName": agent_name, "nonce": nonce, "expiryAfter": expiry_after},
            expiry_after,
        )

    def withdraw(self, destination, amount):
        """Withdraw funds."""
        nonce = int(time.time() * 1000)
        return self._master_sign_and_send(
            {"type": "withdraw", "destination": destination, "amount": amount},
            "Withdraw",
            [{"name": "dexChain", "type": "string"},
             {"name": "destination", "type": "address"},
             {"name": "amount", "type": "string"},
             {"name": "nonce", "type": "uint64"},
             {"name": "expiryAfter", "type": "uint64"}],
            {"dexChain": self.dex_chain, "destination": destination,
             "amount": amount, "nonce": nonce, "expiryAfter": 0},
        )

    def usd_send(self, to, amount):
        """Transfer USD between accounts."""
        nonce = int(time.time() * 1000)
        return self._master_sign_and_send(
            {"type": "usdSend", "to": to, "amount": amount},
            "UsdTransfer",
            [{"name": "dexChain", "type": "string"},
             {"name": "to", "type": "address"},
             {"name": "amount", "type": "string"},
             {"name": "nonce", "type": "uint64"},
             {"name": "expiryAfter", "type": "uint64"}],
            {"dexChain": self.dex_chain, "to": to,
             "amount": amount, "nonce": nonce, "expiryAfter": 0},
        )

    # ═════════════════════════════════════════════════════════════
    #  Public API — Agent signed
    # ═════════════════════════════════════════════════════════════

    def place_order(self, symbol_code, px, qty, side="BUY",
                    ord_type="LIMIT", tif="GTC", **kwargs):
        """Place a single order."""
        order = {
            "symbol_code": symbol_code,
            "ord_px": px,
            "ord_qty": qty,
            "ord_type": ORD_TYPE[ord_type],
            "ord_side": ORD_SIDE[side],
            "time_in_force": ORD_TIF[tif],
        }
        if kwargs.get("reduce_only"):
            order["reduce_only_option"] = REDUCE_ONLY[kwargs["reduce_only"]]
        if kwargs.get("trigger_px"):
            order["trigger_px"] = kwargs["trigger_px"]
        if kwargs.get("trigger_type"):
            order["tpsl_trigger_type"] = TRIGGER_TYPE[kwargs["trigger_type"]]
        if kwargs.get("slippage_pct"):
            order["slippage_pct"] = kwargs["slippage_pct"]
        if kwargs.get("cl_ord_id"):
            order["cl_ord_id"] = kwargs["cl_ord_id"]

        proto = Proto.place_orders([order])
        action = {
            "type": "placeOrder",
            "orders": [{
                "symbolCode": symbol_code, "ordPx": px, "ordQty": qty,
                "ordType": ord_type, "ordSide": side, "timeInForce": tif,
                **{k: v for k, v in kwargs.items()
                   if k in ("reduce_only_option", "triggerPx", "tpslTriggerType",
                            "slippagePct", "clOrdId", "parentOrdId")},
            }],
        }
        return self._agent_sign_and_send(action, proto)

    def cancel_order(self, symbol_code, ord_id=None, cl_ord_id=None):
        """Cancel an order by ordId or clOrdId."""
        cancel = {"symbol_code": symbol_code}
        action_cancel = {"symbolCode": symbol_code}
        if ord_id:
            cancel["ord_id"] = int(ord_id)
            action_cancel["ordId"] = str(ord_id)
        if cl_ord_id:
            cancel["cl_ord_id"] = int(cl_ord_id)
            action_cancel["clOrdId"] = str(cl_ord_id)

        proto = Proto.cancel_orders([cancel])
        return self._agent_sign_and_send(
            {"type": "cancelOrder", "cancels": [action_cancel]}, proto)

    def cancel_all(self, symbol_code, conditional=False):
        """Cancel all orders for a symbol."""
        proto = Proto.cancel_all(symbol_code, conditional)
        return self._agent_sign_and_send(
            {"type": "cancelAll", "symbolCode": symbol_code,
             "conditionalOrder": conditional}, proto)

    def set_leverage(self, symbol_code, leverage):
        """Set leverage for a symbol."""
        proto = Proto.set_leverage(symbol_code, str(leverage))
        return self._agent_sign_and_send(
            {"type": "setLeverage", "symbolCode": symbol_code,
             "leverage": str(leverage)}, proto)

    def set_margin_mode(self, symbol_code, mode):
        """Set margin mode (CROSS / ISOLATED)."""
        proto = Proto.set_margin_mode(symbol_code, MARGIN_MODE[mode])
        return self._agent_sign_and_send(
            {"type": "setMarginMode", "symbolCode": symbol_code,
             "marginMode": mode}, proto)

    def assign_pos_margin(self, symbol_code, amount):
        """Assign margin to isolated position."""
        proto = Proto.assign_pos_margin(symbol_code, str(amount))
        return self._agent_sign_and_send(
            {"type": "assignPosMargin", "symbolCode": symbol_code,
             "assignedPosMargin": str(amount)}, proto)

    def bind_referral(self, code):
        """Bind a referral code."""
        proto = Proto.bind_referral(code)
        return self._agent_sign_and_send(
            {"type": "bindReferral", "referralCode": code}, proto)

    # ── Vault ────────────────────────────────────────────────────

    def vault_create(self, name, description, amount, currency_code=1):
        proto = Proto.vault_create(name, description, str(amount), currency_code)
        return self._agent_sign_and_send(
            {"type": "vaultCreate", "name": name, "description": description,
             "amount": str(amount), "currencyCode": currency_code}, proto)

    def vault_deposit(self, vault_address, amount, currency_code=1):
        proto = Proto.vault_deposit(str(amount), currency_code)
        return self._agent_sign_and_send(
            {"type": "vaultDeposit", "amount": str(amount),
             "currencyCode": currency_code},
            proto, vault_address=vault_address)

    def vault_withdraw(self, vault_address, amount, currency_code=1):
        proto = Proto.vault_withdraw(str(amount), currency_code)
        return self._agent_sign_and_send(
            {"type": "vaultWithdraw", "amount": str(amount),
             "currencyCode": currency_code},
            proto, vault_address=vault_address)

    def vault_close(self, vault_address):
        proto = Proto.vault_close()
        return self._agent_sign_and_send(
            {"type": "vaultClose"}, proto, vault_address=vault_address)

    # ── Info queries ─────────────────────────────────────────────

    def get_products(self):
        return self._get("/info/public/product-meta")

    def get_wallet(self, user_addr=None):
        return self._get("/info/account/wallet",
                         {"userAddr": user_addr or self.master_addr})

    def get_orders(self, user_addr=None, symbol=None):
        params = {"userAddr": user_addr or self.master_addr}
        if symbol:
            params["symbol"] = symbol
        return self._get("/info/order/states", params)

    def get_positions(self, user_addr=None):
        return self._get("/info/position/list",
                         {"userAddr": user_addr or self.master_addr})

    def get_kline(self, symbol_name, interval, limit=100):
        return self._get("/info/kline/last",
                         {"symbol_name": symbol_name, "interval": interval,
                          "limit": limit})

    # ── WebSocket ────────────────────────────────────────────────

    async def subscribe(self, subscription, callback, timeout=10):
        """Subscribe to a WebSocket channel. Calls callback(msg) for each push."""
        import websockets
        async with websockets.connect(self.ws_url, close_timeout=5) as ws:
            await ws.send(json.dumps({
                "method": "subscribe", "subscription": subscription,
            }))
            deadline = time.time() + timeout
            while time.time() < deadline:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=3)
                    msg = json.loads(raw)
                    if msg.get("channel") == "pong":
                        continue
                    if msg.get("method") == "subscribe":
                        continue
                    if callback(msg) is False:
                        break
                except asyncio.TimeoutError:
                    continue


# ═══════════════════════════════════════════════════════════════════
#  Quick Test (run this file directly)
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    master = Account.create()
    agent = Account.create()

    print(f"Master: {master.address}")
    print(f"Agent:  {agent.address}")

    client = DexClient(
        master_key=master.key.hex(),
        agent_key=agent.key.hex(),
        testnet=True,
    )

    # 1. Faucet
    print("\n1. faucetClaim:", json.dumps(client.faucet_claim()))
    time.sleep(2)

    # 2. Approve agent
    print("2. approveAgent:", json.dumps(client.approve_agent()))
    time.sleep(2)

    # 3. Place order
    print("3. placeOrder:", json.dumps(
        client.place_order(symbol_code=1, px="1.0", qty="0.001", side="BUY")))

    # 4. WebSocket
    print("\n4. WebSocket orderBook:")
    count = [0]
    def on_data(msg):
        print(f"   received: {json.dumps(msg)[:200]}")
        count[0] += 1
        return False  # stop after first message

    asyncio.run(client.subscribe(
        {"type": "orderBook", "symbol": "BTCUSDC", "depth": 5}, on_data))

    print("\nAll tests done.")
