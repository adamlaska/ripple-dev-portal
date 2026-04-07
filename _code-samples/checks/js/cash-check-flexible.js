import xrpl from 'xrpl'

// Define parameters. Edit this code with your values before running it.
const secret = "s████████████████████████████"
// Replace with your secret
const check_id = "" // Replace with your Check ID
const deliver_min = "20000000" // Replace with the minimum amount to receive
               // String for XRP in drops
               // {currency, issuer, value} object for token amount

// Connect to Testnet ----------------------
const client = new xrpl.Client("wss://s.altnet.rippletest.net:51233")
await client.connect()

// Instantiate a wallet ----------------------
const wallet = xrpl.Wallet.fromSeed(secret)
console.log("Wallet address: ", wallet.address)

// Check if the check ID is provided ----------------------
if (check_id.length === 0) {
  console.log("Please edit this snippet to provide a check ID. You can get a check ID by running create-check.js.")
  process.exit(1)
}

// Prepare the transaction ----------------------
const checkcash = {
  TransactionType: "CheckCash",
  Account: wallet.address,
  CheckID: check_id,
  DeliverMin: deliver_min
}

// Submit the transaction ----------------------
const tx = await client.submitAndWait(
  checkcash,
  { autofill: true,
    wallet: wallet }
)

// Confirm transaction results ----------------------
console.log(`Transaction result: ${JSON.stringify(tx, null, 2)}`)

if (tx.result.meta.TransactionResult === "tesSUCCESS") {
  // submitAndWait() only returns when the transaction's outcome is final,
  // so you don't also have to check for validated: true.
  console.log("Transaction was successful.")

  console.log("Balance changes:",
    JSON.stringify(xrpl.getBalanceChanges(tx.result.meta), null, 2)
  )
}

// Disconnect ----------------------
await client.disconnect()
