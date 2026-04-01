
# Set up client ----------------------

from xrpl.clients import JsonRpcClient

client = JsonRpcClient("https://s.devnet.rippletest.net:51234")

# Look up reserve values ----------------------

from xrpl.models.requests import ServerInfo

response = client.request(ServerInfo())
validated_ledger = response.result["info"]["validated_ledger"]

base_reserve = validated_ledger["reserve_base_xrp"]
reserve_inc = validated_ledger["reserve_inc_xrp"]

print(f"Base reserve: {base_reserve} XRP")
print(f"Incremental reserve: {reserve_inc} XRP")

# Look up owner count ----------------------

from xrpl.models.requests import AccountInfo

address = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"  # replace with any address
response = client.request(AccountInfo(account=address))
owner_count = response.result["account_data"]["OwnerCount"]

# Calculate total reserve ----------------------

total_reserve = base_reserve + (owner_count * reserve_inc)

print(f"Owner count: {owner_count}")
print(f"Total reserve: {total_reserve} XRP")