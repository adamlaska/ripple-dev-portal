import xrpl from 'xrpl'
import { execSync } from 'child_process'
import fs from 'fs'

// Auto-run setup if needed ----------------------

if (!fs.existsSync('checks-setup.json')) {
  execSync('node checks-setup.js', { stdio: 'inherit' })
}

// Define parameters ----------------------

const setupData = JSON.parse(fs.readFileSync('checks-setup.json', 'utf8'))
const wallet = xrpl.Wallet.fromSeed(setupData.recipient.seed)
const check_id = setupData.checkIDs.flexible
const deliver_min = xrpl.xrpToDrops(20)

// Connect to Testnet ----------------------

const client = new xrpl.Client("wss://s.altnet.rippletest.net:51233")
await client.connect()

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
