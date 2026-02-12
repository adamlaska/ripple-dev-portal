# IMPORTANT: This example creates a loan using a preconfigured
# loan broker, borrower, and private vault.

import asyncio
import json
import os
import subprocess
import sys

from xrpl.asyncio.clients import AsyncWebsocketClient
from xrpl.asyncio.transaction import autofill
from xrpl.models import LoanSet, Sign, SubmitOnly, Transaction, Tx
from xrpl.wallet import Wallet


async def main():
    # Connect to the network ----------------------
    async with AsyncWebsocketClient("wss://s.devnet.rippletest.net:51233") as client:

        # This step checks for the necessary setup data to run the lending protocol tutorials.
        # If missing, lending_setup.py will generate the data.
        if not os.path.exists("lending_setup.json"):
            print("\n=== Lending tutorial data doesn't exist. Running setup script... ===\n")
            subprocess.run([sys.executable, "lending_setup.py"], check=True)

        # Load preconfigured accounts and loan_broker_id.
        with open("lending_setup.json") as f:
            setup_data = json.load(f)

        # You can replace these values with your own.
        loan_broker = Wallet.from_seed(setup_data["loan_broker"]["seed"])
        borrower = Wallet.from_seed(setup_data["borrower"]["seed"])
        loan_broker_id = setup_data["loan_broker_id"]

        print(f"\nLoan broker address: {loan_broker.address}")
        print(f"Borrower address: {borrower.address}")
        print(f"LoanBrokerID: {loan_broker_id}")

        # Prepare LoanSet transaction ----------------------
        # Account and Counterparty accounts can be swapped, but determines signing order.
        # Account signs first, Counterparty signs second.
        print("\n=== Preparing LoanSet transaction ===\n")

        loan_set_tx = await autofill(LoanSet(
            account=loan_broker.address,
            counterparty=borrower.address,
            loan_broker_id=loan_broker_id,
            principal_requested="1000",
            interest_rate=500,
            payment_total=12,
            payment_interval=2592000,
            grace_period=604800,
            loan_origination_fee="100",
            loan_service_fee="10",
        ), client)

        print(json.dumps(loan_set_tx.to_xrpl(), indent=2))

        # Loan broker signs first.
        print("\n=== Adding loan broker signature ===\n")
        loan_broker_signature = await client.request(Sign(
            transaction=loan_set_tx,
            secret=loan_broker.seed,
        ))

        loan_broker_signature_result = loan_broker_signature.result["tx_json"]

        print(f"TxnSignature: {loan_broker_signature_result['TxnSignature']}")
        print(f"SigningPubKey: {loan_broker_signature_result['SigningPubKey']}\n")
        print(f"Signed loan_set_tx for borrower to sign over:\n{json.dumps(loan_broker_signature_result, indent=2)}")
        
        # Borrower signs second.
        print("\n=== Adding borrower signature ===\n")
        borrower_signature = await client.request(Sign(
            transaction=Transaction.from_xrpl(loan_broker_signature_result),
            secret=borrower.seed,
            signature_target="CounterpartySignature",
        ))

        borrower_signature_result = borrower_signature.result["tx_json"]

        print(f"Borrower TxnSignature: {borrower_signature_result['CounterpartySignature']['TxnSignature']}")
        print(f"Borrower SigningPubKey: {borrower_signature_result['CounterpartySignature']['SigningPubKey']}")

        print(f"\nFully signed LoanSet transaction:\n{json.dumps(borrower_signature_result, indent=2)}")

        # Submit and wait for validation ----------------------
        print("\n=== Submitting signed LoanSet transaction ===\n")

        # Submit the transaction
        submit_result = await client.request(
            SubmitOnly(tx_blob=borrower_signature.result["tx_blob"])
        )
        tx_hash = submit_result.result["tx_json"]["hash"]

        # Helper function to check tx hash is validated
        async def validate_tx(hash, max_retries=20):
            for _ in range(max_retries):
                await asyncio.sleep(1)
                try:
                    response = await client.request(Tx(transaction=hash))
                    if response.result.get("validated"):
                        return response
                except Exception:
                    pass  # Transaction not validated yet, check again
            raise Exception(
                f"Transaction {hash} not validated after {max_retries} attempts."
            )

        # Validate the transaction
        submit_response = await validate_tx(tx_hash)

        if submit_response.result["meta"]["TransactionResult"] != "tesSUCCESS":
            result_code = submit_response.result["meta"]["TransactionResult"]
            print(f"Error: Unable to create loan: {result_code}")
            sys.exit(1)

        print("Loan created successfully!")

        # Extract loan information from the transaction result.
        print("\n=== Loan Information ===\n")
        loan_node = next(
            node for node in submit_response.result["meta"]["AffectedNodes"]
            if node.get("CreatedNode", {}).get("LedgerEntryType") == "Loan"
        )
        print(json.dumps(loan_node["CreatedNode"]["NewFields"], indent=2))


asyncio.run(main())
