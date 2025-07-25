import asyncio
import json
import os
from ic.client import Client
from ic.identity import Identity
from ic.agent import Agent
from ic.candid import encode, decode, Types


def get_canister_id(name="scraper"):
    """
    Loads the canister ID from canister_ids.json based on DFX_NETWORK
    """
    network = os.getenv("DFX_NETWORK", "local")
    with open("canister_ids.json") as f:
        ids = json.load(f)
    return ids[name][network]


async def fetch_from_icp(url: str) -> str:
    """
    Queries the 'scraper' ICP canister to fetch page HTML content
    """
    canister_id = get_canister_id("scraper")

    identity = Identity.anonymous()
    client = Client(url="http://127.0.0.1:4943")  # or https://ic0.app for mainnet
    agent = Agent(identity, client)
    await agent.fetch_root_key()  

    args = encode([Types.Text], [url])
    response = await agent.query_raw(canister_id, "fetch_page", args)

    result = decode([Types.Text], response)
    return result[0]
