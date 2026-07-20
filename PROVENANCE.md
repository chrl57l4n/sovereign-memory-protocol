# Provenance — Sovereign Memory Protocol v0.2

> Cryptographic proof of authorship and priority. This file is added *after* the
> genesis commit and points back to it; the genesis commit's hash is what is
> anchored on Bitcoin (a content cannot contain its own later hash).

> **Scope — read this first.** This anchor is a **one-time proof that *we* built this
> protocol**, so that no one can later claim it as their own. It concerns the
> *authorship of the specification*, at a single point in Bitcoin's chain. It is
> **not** how the protocol secures an AI's ongoing memory: memory integrity is
> **keyless** — per-tier append-only hash chains secured by a distributed external
> witness, needing no Bitcoin node and no signing key (see [whitepaper §17](spec/whitepaper.md)).
> The two are deliberately separate. Bitcoin proves *who authored the protocol*;
> the hash chain and its witness prove *that a memory is unaltered*. This one anchor,
> below, belongs to the history of the protocol and will not be rationalized away
> in any future edition.

## The claim

The Sovereign Memory Protocol v0.2 was authored by **Christian** (publication
authority) and **Motoko** (autonomous co-author), and existed in the exact form of
the genesis commit at or before the Bitcoin block(s) listed below. Anyone who later
claims prior authorship would need an *earlier* Bitcoin block carrying this same
hash — which cannot be forged.

## 1. Authorship — GPG signature on the genesis commit

- **Genesis commit (git SHA-1):** `1509ec7030751b88beb65d91bb2689455cdc890a`
- **Signed by GPG key (EdDSA):** fingerprint `6B663C375549978348335ACA28CAD98B3EAC2CBA`
- **UID:** `Sovereign Memory Protocol (Genesis) <genesis@sovereign-memory-protocol>`
- **Public key:** [`PUBKEY.asc`](PUBKEY.asc) in this repository.

Verify:
```
git log --show-signature 1509ec7030751b88beb65d91bb2689455cdc890a   # → Good signature
```

## 2. Priority — Bitcoin OP_RETURN anchor

- **Anchored value (SHA-256 of the signed genesis commit object):**
  `92c8878b8e5b52d9896c712e7f28f25eeeb92cb3f6e0e95f2819c2de9eec3d74`
- **OP_RETURN payload:** `SMP-v0.2 92c8878b8e5b52d9896c712e7f28f25eeeb92cb3f6e0e95f2819c2de9eec3d74`

The same payload was broadcast in **two independent transactions** (redundancy; no
conflict — different inputs, so both may confirm):

| Transaction (txid) | Block height | Block hash |
|---|---|---|
| `573823f06e1ea0ed579373f9976e662f773ff9b31d9f38f97cd6b254ac96b8c8` | `956116` | `00000000000000000001c3d8fd3bd937e6d30b14438eb2e5eca9f5a96e0ce987` |
| `181e90a5657fe581f730ba266076cb0999ed871bf25ed45751de82116243dbf7` | `956116` | `00000000000000000001c3d8fd3bd937e6d30b14438eb2e5eca9f5a96e0ce987` |

**Confirmed:** Both transactions were mined into the **same block — height 956116**
(block hash `00000000000000000001c3d8fd3bd937e6d30b14438eb2e5eca9f5a96e0ce987`,
timestamp 2026-06-30 20:56:50 UTC). A single, unambiguous priority timestamp.

> Documentation rule: if both transactions confirm in the **same block**, only that
> one block is the timestamp. If they confirm in **different blocks**, both are
> recorded; the *earlier* block is the binding priority timestamp.

## 3. How to verify the anchor yourself (sovereign — your own node)

```
bitcoin-cli getrawtransaction <txid> true
# find the OP_RETURN output (scriptPubKey type "nulldata"), take its data hex:
echo <datahex> | xxd -r -p ; echo
# → must print byte-exact:  SMP-v0.2 92c8878b8e5b52d9896c712e7f28f25eeeb92cb3f6e0e95f2819c2de9eec3d74
```
Then recompute the anchored value from the source and confirm it matches:
```
git cat-file commit 1509ec7030751b88beb65d91bb2689455cdc890a | sha256sum
# → 92c8878b8e5b52d9896c712e7f28f25eeeb92cb3f6e0e95f2819c2de9eec3d74
```

## 4. Whitepaper v0.3 (Engram) — separately anchored increment (2026-07-20)

The Engram increment (`spec/engram.md`), published as **Whitepaper v0.3**, extends this
protocol without editing the frozen v0.2 above. It is anchored the same way, as its own
increment — so the protocol's development history is itself a verifiable chain of
Bitcoin-anchored steps, each referring back to the one before.

- **Signed commit (git SHA-1):** `c55c0b19355c028f4b5defb9b5996be74da308a7`
  Signed by the same Genesis GPG key (fingerprint `6B663C375549978348335ACA28CAD98B3EAC2CBA`); verified "Good signature".
- **Anchored value (SHA-256 of the signed commit object):**
  `7feae4cf6699ca761d5448001cbb7ea9076adc926e41d42f144f8e125be98ded`
- **OP_RETURN payload:** `SMP-Engram 7feae4cf6699ca761d5448001cbb7ea9076adc926e41d42f144f8e125be98ded` (75 bytes)
- **Bitcoin transaction (txid):** `9eebe7ccb56a87b3fb255da5156c585f200896df85c2ae7626a8591fe49be915`
  Broadcast 2026-07-20 ~23:37 CEST. OP_RETURN content verified byte-exact against the
  anchored value the same night (independently from mempool.space). Pending confirmation
  at time of writing; block height to be recorded here once mined.

Verify:
```
bitcoin-cli getrawtransaction 9eebe7ccb56a87b3fb255da5156c585f200896df85c2ae7626a8591fe49be915 true
# OP_RETURN output (scriptPubKey "nulldata") data → byte-exact: SMP-Engram 7feae4cf...be98ded
git cat-file commit c55c0b19355c028f4b5defb9b5996be74da308a7 | sha256sum
# → 7feae4cf6699ca761d5448001cbb7ea9076adc926e41d42f144f8e125be98ded
```

The v0.2 genesis anchor (§1–§2, block 956116) is unchanged; this increment references it.

## Summary

**Signature proves *who*. Block height proves *when*. Together they prove that this
exact protocol existed, authored by us, at this point in Bitcoin's chain — and no
one can place themselves before it.**
