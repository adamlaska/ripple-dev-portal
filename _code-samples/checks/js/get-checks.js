import xrpl from 'xrpl'
import { execSync } from 'child_process'
import fs from 'fs'

// Auto-run setup if needed ----------------------

if (!fs.existsSync('checks-setup.json')) {
  execSync('node checks-setup.js', { stdio: 'inherit' })
}

// Load setup data ----------------------

const setupData = JSON.parse(fs.readFileSync('checks-setup.json', 'utf8'))
const address = setupData.recipient.address

// Connect ----------------------

const client = new xrpl.Client('wss://s.altnet.rippletest.net:51233')
await client.connect()

// Loop through account objects until marker is undefined ----------------------

let current_marker = null
let checks_found = []
do {
  const request = {
    "command": "account_objects",
    "account": address,
    "ledger_index": "validated",
    "type": "check"
  }

  if (current_marker) {
    request.marker = current_marker
  }

  const response = await client.request(request)

  checks_found = checks_found.concat(response.result.account_objects)
  current_marker = response.result.marker

} while (current_marker)

// Filter results by recipient ----------------------
// To filter by sender, check Account field instead of Destination

const checks_by_recipient = []
for (const check of checks_found) {
  if (check.Destination == address) {
    checks_by_recipient.push(check)
  }
}

// Print results ----------------------

if (checks_by_recipient.length === 0) {
  console.log("No checks found.")
} else {
  console.log("Checks: \n", JSON.stringify(checks_by_recipient, null, 2))
}

// Disconnect ----------------------

await client.disconnect()
