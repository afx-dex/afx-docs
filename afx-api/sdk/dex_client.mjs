/**
 * AFX DEX JavaScript SDK
 *
 * Lightweight client for the AFX DEX API. Handles EIP-712 signing,
 * protobuf serialization, and HTTP requests.
 *
 * Dependencies:
 *   npm install ethers protobufjs ws
 *
 * Usage:
 *   import { DexClient } from "./dex_client.mjs";
 *
 *   const client = await DexClient.create({
 *     masterKey: "0x...",
 *     agentKey:  "0x...",
 *     testnet:   true,
 *   });
 *   await client.faucetClaim();
 *   await client.approveAgent();
 *   await client.placeOrder({ symbolCode: 1, px: "40000", qty: "0.5", side: "BUY" });
 */

import { ethers } from "ethers";
import protobuf from "protobufjs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

// ═══════════════════════════════════════════════════════════════════
//  Config
// ═══════════════════════════════════════════════════════════════════

const ENVS = {
  mainnet: {
    baseUrl: "https://api10.afx.xyz",
    wsUrl: "wss://ws10.afx.xyz/ws/dex",
    chainId: 42161,
    source: "a",
    dexChain: "Mainnet",
  },
  testnet: {
    baseUrl: "https://api10-testnet.afx.xyz",
    wsUrl: "wss://ws10-testnet.afx.xyz/ws/dex",
    chainId: 421614,
    source: "b",
    dexChain: "Testnet",
  },
};

const ZERO_ADDR = "0x" + "0".repeat(40);

const ORD_TYPE = { LIMIT: 1, MARKET: 2 };
const ORD_SIDE = { BUY: 1, SELL: 2, BUY_CLOSE_HEDGE: 3, SELL_CLOSE_HEDGE: 4 };
const ORD_TIF = { GTC: 1, IOC: 2, FOK: 3, POST_ONLY: 4 };
const REDUCE_ONLY = { REDUCE_ONLY: 1, TP_FROM_POSITION: 2, SL_FROM_POSITION: 3 };
const TRIGGER_TYPE = { LAST_PRICE: 1, MARK_PRICE: 2, INDEX_PRICE: 3 };
const MARGIN_MODE_MAP = { CROSS: 1, ISOLATED: 2 };

// ═══════════════════════════════════════════════════════════════════
//  DexClient
// ═══════════════════════════════════════════════════════════════════

export class DexClient {
  /**
   * Create a new client. Use `await DexClient.create(opts)` to auto-load proto.
   */
  static async create({ masterKey, agentKey, testnet = true, protoPath }) {
    const client = new DexClient({ masterKey, agentKey, testnet });
    const dir = dirname(fileURLToPath(import.meta.url));
    const path = protoPath || join(dir, "dex.proto");
    client.root = await protobuf.load(path);
    return client;
  }

  constructor({ masterKey, agentKey, testnet = true }) {
    const env = testnet ? ENVS.testnet : ENVS.mainnet;
    Object.assign(this, env);

    this.master = new ethers.Wallet(masterKey);
    this.agent = new ethers.Wallet(agentKey);
    this.root = null; // loaded via create()
  }

  // ── Low-level ──────────────────────────────────────────────────

  async _post(body) {
    const resp = await fetch(`${this.baseUrl}/api/v1/exchange`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return resp.json();
  }

  async _get(path, params = {}) {
    const qs = new URLSearchParams(params).toString();
    const resp = await fetch(`${this.baseUrl}${path}?${qs}`);
    return resp.json();
  }

  _encode(msgType, payload) {
    const Msg = this.root.lookupType(msgType);
    return Msg.encode(Msg.create(payload)).finish();
  }

  // ── Agent signing ──────────────────────────────────────────────

  async _agentSignAndSend(action, protoBytes, { vaultAddress, expiryAfter = 0 } = {}) {
    const nonce = Date.now();
    const parts = [Buffer.from(protoBytes)];
    if (vaultAddress) parts.push(Buffer.from(vaultAddress.slice(2), "hex"));

    const nonceBuf = Buffer.alloc(8);
    nonceBuf.writeBigUInt64LE(BigInt(nonce));
    parts.push(nonceBuf);

    const expiryBuf = Buffer.alloc(8);
    expiryBuf.writeBigUInt64LE(BigInt(expiryAfter));
    parts.push(expiryBuf);

    const connectionId = ethers.keccak256(Buffer.concat(parts));

    const sig = await this.agent.signTypedData(
      { name: "Exchange", version: "1", chainId: this.chainId, verifyingContract: ZERO_ADDR },
      { Agent: [{ name: "source", type: "string" }, { name: "connectionId", type: "bytes32" }] },
      { source: this.source, connectionId },
    );
    const { r, s, v } = ethers.Signature.from(sig);

    return this._post({
      action, signature: { r, s, v }, nonce,
      expiryAfter: expiryAfter || null,
      vaultAddress: vaultAddress || null,
    });
  }

  // ── Master signing ─────────────────────────────────────────────

  async _masterSignAndSend(action, primaryType, types, message, { expiryAfter = 0 } = {}) {
    const nonce = Date.now();
    const sig = await this.master.signTypedData(
      { name: "SignTransaction", version: "1", chainId: this.chainId, verifyingContract: ZERO_ADDR },
      { [primaryType]: types },
      message,
    );
    const { r, s, v } = ethers.Signature.from(sig);

    return this._post({
      action, signature: { r, s, v }, nonce,
      expiryAfter: expiryAfter || null,
    });
  }

  // ═══════════════════════════════════════════════════════════════
  //  Public API — Master signed
  // ═══════════════════════════════════════════════════════════════

  async faucetClaim() {
    return this._masterSignAndSend(
      { type: "faucetClaim" },
      "TestnetFaucetClaim",
      [{ name: "dexChain", type: "string" }],
      { dexChain: "Testnet" },
    );
  }

  async approveAgent({ agentName = "default", expirySeconds = 300 } = {}) {
    const nonce = Date.now();
    const expiryAfter = Math.floor(Date.now() / 1000) + expirySeconds;
    return this._masterSignAndSend(
      { type: "approveAgent", agentAddress: this.agent.address,
        agentName, dexChain: this.dexChain },
      "ApproveAgent",
      [{ name: "dexChain", type: "string" }, { name: "agentAddress", type: "address" },
       { name: "agentName", type: "string" }, { name: "nonce", type: "uint64" },
       { name: "expiryAfter", type: "uint64" }],
      { dexChain: this.dexChain, agentAddress: this.agent.address,
        agentName, nonce, expiryAfter },
      { expiryAfter },
    );
  }

  async withdraw({ destination, amount }) {
    const nonce = Date.now();
    return this._masterSignAndSend(
      { type: "withdraw", destination, amount },
      "Withdraw",
      [{ name: "dexChain", type: "string" }, { name: "destination", type: "address" },
       { name: "amount", type: "string" }, { name: "nonce", type: "uint64" },
       { name: "expiryAfter", type: "uint64" }],
      { dexChain: this.dexChain, destination, amount, nonce, expiryAfter: 0 },
    );
  }

  async usdSend({ to, amount }) {
    const nonce = Date.now();
    return this._masterSignAndSend(
      { type: "usdSend", to, amount },
      "UsdTransfer",
      [{ name: "dexChain", type: "string" }, { name: "to", type: "address" },
       { name: "amount", type: "string" }, { name: "nonce", type: "uint64" },
       { name: "expiryAfter", type: "uint64" }],
      { dexChain: this.dexChain, to, amount, nonce, expiryAfter: 0 },
    );
  }

  // ═══════════════════════════════════════════════════════════════
  //  Public API — Agent signed
  // ═══════════════════════════════════════════════════════════════

  async placeOrder({ symbolCode, px, qty, side = "BUY", ordType = "LIMIT",
                     tif = "GTC", ...opts }) {
    const proto = this._encode("MsgPlaceOrders", {
      orders: [{
        symbolCode, ordPx: px, ordQty: qty,
        ordType: ORD_TYPE[ordType], ordSide: ORD_SIDE[side], timeInForce: ORD_TIF[tif],
        ...(opts.reducOnly && { reduceOnlyOption: REDUCE_ONLY[opts.reduceOnly] }),
        ...(opts.triggerPx && { triggerPx: opts.triggerPx }),
        ...(opts.triggerType && { tpslTriggerType: TRIGGER_TYPE[opts.triggerType] }),
        ...(opts.slippagePct && { slippagePct: opts.slippagePct }),
      }],
    });
    return this._agentSignAndSend({
      type: "placeOrder",
      orders: [{ symbolCode, ordPx: px, ordQty: qty, ordType, ordSide: side, timeInForce: tif,
        ...opts }],
    }, proto);
  }

  async cancelOrder({ symbolCode, ordId, clOrdId }) {
    const proto = this._encode("MsgCancelOrders", {
      orders: [{ symbolCode, ...(ordId && { ordId: +ordId }), ...(clOrdId && { clOrdId: +clOrdId }) }],
    });
    return this._agentSignAndSend({
      type: "cancelOrder",
      cancels: [{ symbolCode, ...(ordId && { ordId: String(ordId) }),
        ...(clOrdId && { clOrdId: String(clOrdId) }) }],
    }, proto);
  }

  async cancelAll({ symbolCode, conditional = false }) {
    const proto = this._encode("MsgCancelAll", { symbolCode, isConditionalOrder: conditional });
    return this._agentSignAndSend(
      { type: "cancelAll", symbolCode, conditionalOrder: conditional }, proto);
  }

  async setLeverage({ symbolCode, leverage }) {
    const proto = this._encode("MsgSetLeverage", { symbolCode, leverage: String(leverage) });
    return this._agentSignAndSend(
      { type: "setLeverage", symbolCode, leverage: String(leverage) }, proto);
  }

  async setMarginMode({ symbolCode, mode }) {
    const proto = this._encode("MsgSetMarginMode", { symbolCode, marginMode: MARGIN_MODE_MAP[mode] });
    return this._agentSignAndSend(
      { type: "setMarginMode", symbolCode, marginMode: mode }, proto);
  }

  async assignPosMargin({ symbolCode, amount }) {
    const proto = this._encode("MsgAssignPosMargin", { symbolCode, assignedPosMargin: String(amount) });
    return this._agentSignAndSend(
      { type: "assignPosMargin", symbolCode, assignedPosMargin: String(amount) }, proto);
  }

  async bindReferral({ code }) {
    const proto = this._encode("MsgBindReferral", { referralCode: code });
    return this._agentSignAndSend({ type: "bindReferral", referralCode: code }, proto);
  }

  // ── Vault ──────────────────────────────────────────────────────

  async vaultCreate({ name, description, amount, currencyCode = 1 }) {
    const proto = this._encode("MsgVaultCreate", { name, description, amount: String(amount), currencyCode });
    return this._agentSignAndSend(
      { type: "vaultCreate", name, description, amount: String(amount), currencyCode }, proto);
  }

  async vaultDeposit({ vaultAddress, amount, currencyCode = 1 }) {
    const proto = this._encode("MsgVaultDeposit", { amount: String(amount), currencyCode });
    return this._agentSignAndSend(
      { type: "vaultDeposit", amount: String(amount), currencyCode },
      proto, { vaultAddress });
  }

  async vaultWithdraw({ vaultAddress, amount, currencyCode = 1 }) {
    const proto = this._encode("MsgVaultWithdraw", { amount: String(amount), currencyCode });
    return this._agentSignAndSend(
      { type: "vaultWithdraw", amount: String(amount), currencyCode },
      proto, { vaultAddress });
  }

  async vaultClose({ vaultAddress }) {
    const proto = this._encode("MsgVaultClose", {});
    return this._agentSignAndSend({ type: "vaultClose" }, proto, { vaultAddress });
  }

  // ── Info queries ───────────────────────────────────────────────

  async getProducts() { return this._get("/info/public/product-meta"); }
  async getWallet(userAddr) { return this._get("/info/account/wallet", { userAddr: userAddr || this.master.address }); }
  async getOrders(userAddr) { return this._get("/info/order/states", { userAddr: userAddr || this.master.address }); }
  async getPositions(userAddr) { return this._get("/info/position/list", { userAddr: userAddr || this.master.address }); }
  async getKline(symbolName, interval, limit = 100) {
    return this._get("/info/kline/last", { symbol_name: symbolName, interval, limit });
  }

  // ── WebSocket ──────────────────────────────────────────────────

  async subscribe(subscription, callback, { timeout = 10000 } = {}) {
    const WebSocket = (await import("ws")).default;
    return new Promise((resolve) => {
      const ws = new WebSocket(this.wsUrl);
      const timer = setTimeout(() => { ws.close(); resolve(); }, timeout);

      ws.on("open", () => {
        ws.send(JSON.stringify({ method: "subscribe", subscription }));
      });

      ws.on("message", (data) => {
        const msg = JSON.parse(data.toString());
        if (msg.channel === "pong" || msg.method === "subscribe") return;
        if (callback(msg) === false) {
          clearTimeout(timer);
          ws.close();
          resolve();
        }
      });

      ws.on("error", () => { clearTimeout(timer); resolve(); });
    });
  }
}
