import xrpl from 'xrpl'
import { execSync } from 'child_process'
import fs from 'fs'

// Auto-run setup if needed ----------------------

if (!fs.existsSync('checks-setup.json')) {
  execSync('node checks-setup.js', { stdio: 'inherit' })
}

// Load setup data ----------------------

const setupData = JSON.parse(fs.readFileSync('checks-setup.json', 'utf8'))
const wallet = xrpl.Wallet.fromSeed(setupData.sender.seed)
const check_id = setupData.checkIDs.cancel

// Connect ----------------------

const client = new xrpl.Client('wss://s.altnet.rippletest.net:51233')
await client.connect()

// Prepare the transaction ----------------------

const checkcancel = {
  "TransactionType": "CheckCancel",
  "Account": wallet.address,
  "CheckID": check_id
}

// Submit the transaction ----------------------

const tx = await client.submitAndWait(
  checkcancel,
  { autofill: true,
    wallet: wallet }
)

// Confirm results ----------------------

console.log(`Transaction result: ${JSON.stringify(tx, null, 2)}`)

if (tx.result.meta.TransactionResult === "tesSUCCESS") {
  // submitAndWait() only returns when the transaction's outcome is final,
  // so you don't also have to check for validated: true.
  console.log("Transaction was successful.")
}

// Disconnect ----------------------

await client.disconnect()
