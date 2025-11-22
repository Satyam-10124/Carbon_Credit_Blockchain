"""
Algorand NFT Minting Module for Carbon Credits
Mints ARC-69 NFTs to represent verified carbon offset actions
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Tuple, Optional

from algosdk import mnemonic, account
from algosdk.v2client import algod
from algosdk.transaction import AssetConfigTxn, wait_for_confirmation


# ---------- Client & Account ----------

def get_algod_client() -> algod.AlgodClient:
    url = (os.getenv("ALGOD_URL") or os.getenv("ALGORAND_API_URL") or "").strip()
    if not url:
        raise RuntimeError("ALGOD_URL is required (e.g., https://testnet-api.algonode.cloud)")
    api_key = (os.getenv("ALGOD_API_KEY") or "").strip()
    headers = {"X-API-Key": api_key} if api_key else {}
    return algod.AlgodClient(api_key, url, headers=headers)


def get_algorand_account() -> Tuple[str, bytes]:
    seed = (os.getenv("ALGO_MNEMONIC") or os.getenv("ALGORAND_MNEMONIC") or "").strip()
    if not seed:
        raise RuntimeError("ALGO_MNEMONIC is required (25-word mnemonic of a funded TestNet wallet)")
    sk = mnemonic.to_private_key(seed)
    addr = account.address_from_private_key(sk)
    return addr, sk


# ---------- ARC-69 ----------

def _build_arc69_note(image_url: str, asset_name: str, properties: Optional[Dict[str, Any]] = None) -> bytes:
    note = {
        "standard": "arc69",
        "mediaType": "image/jpeg",
        "image": image_url,
        "properties": properties or {},
        "description": "Carbon Credit NFT - Verified environmental action",
        "name": asset_name,
    }
    return json.dumps(note, separators=(",", ":")).encode("utf-8")


def mint_arc69(
    image_url: str,
    asset_name: str,
    unit_name: str,
    properties: Optional[Dict[str, Any]] = None,
) -> Tuple[str, int]:
    """
    Mint an Algorand ASA as an ARC-69 style NFT (total=1, decimals=0) and return (txid, asset_id).
    Uses ALGOD_URL / ALGOD_API_KEY / ALGO_MNEMONIC from the environment.
    """
    if not image_url:
        raise RuntimeError("NFT image URL missing. Set NFT_IMAGE_URL or pass image_url explicitly.")
    if len(image_url.encode("utf-8")) > 96:
        raise RuntimeError(
            f"ASA url too long ({len(image_url.encode('utf-8'))} bytes). Use a short ipfs://CID or shorter gateway URL."
        )

    client = get_algod_client()
    addr, sk = get_algorand_account()

    sp = client.suggested_params()
    note = _build_arc69_note(image_url, asset_name, properties)

    txn = AssetConfigTxn(
        sender=addr,
        sp=sp,
        total=1,
        default_frozen=False,
        unit_name=unit_name,
        asset_name=asset_name,
        manager=addr,
        reserve=addr,
        freeze=addr,
        clawback=addr,
        url=image_url,
        decimals=0,
        strict_empty_address_check=False,
        note=note,
    )
    stx = txn.sign(sk)
    txid = client.send_transaction(stx)
    wait_for_confirmation(client, txid, 4)
    pinfo = client.pending_transaction_info(txid)
    asset_id = pinfo.get("asset-index")
    if not asset_id:
        raise RuntimeError("Mint succeeded but asset-id missing in pending info")
    return txid, int(asset_id)


def mint_carbon_credit_nft(
    trees_planted: int,
    location: str,
    gps_coords: str,
    worker_id: str,
    gesture_signature: str,
    image_url: str = None
) -> Dict[str, Any]:
    """
    Mint a carbon credit NFT with specific properties for environmental actions.
    
    Args:
        trees_planted: Number of trees planted
        location: Location name
        gps_coords: GPS coordinates
        worker_id: Worker identifier
        gesture_signature: Biometric gesture hash
        image_url: URL to verification image (uses NFT_IMAGE_URL from env if not provided)
    
    Returns:
        Dict with transaction ID, asset ID, and metadata
    """
    # Use environment variable if image_url not provided
    if not image_url:
        image_url = os.getenv("NFT_IMAGE_URL", "https://gateway.pinata.cloud/ipfs/bafybeif5ew2ao2pwio75aiuxpsaooeydiworkj7ubrdaycpa6rrwmmuxuu")
    
    properties = {
        "trees_planted": trees_planted,
        "location": location,
        "gps_coordinates": gps_coords,
        "worker_id": worker_id,
        "gesture_signature": gesture_signature,
        "verification_method": "hand_gesture_biometric",
        "timestamp": None,  # Will be added by blockchain
        "carbon_offset_kg": trees_planted * 21.77  # Avg CO2 absorbed per tree per year
    }
    
    asset_name = f"Carbon-{trees_planted}Trees"
    unit_name = "CARBON"
    
    txid, asset_id = mint_arc69(
        image_url=image_url,
        asset_name=asset_name,
        unit_name=unit_name,
        properties=properties
    )
    
    return {
        "transaction_id": txid,
        "asset_id": asset_id,
        "properties": properties,
        "explorer_url": f"https://testnet.algoexplorer.io/asset/{asset_id}"
    }
