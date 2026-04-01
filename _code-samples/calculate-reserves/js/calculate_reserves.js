
// Set up client ----------------------

import xrpl from 'xrpl'

const client = new xrpl.Client('wss://s.devnet.rippletest.net:51233')
await client.connect()

// Look up reserve values ----------------------

const serverInfo = await client.request({ command: 'server_info' })
const validatedLedger = serverInfo.result.info.validated_ledger

const baseReserve = validatedLedger.reserve_base_xrp
const reserveInc = validatedLedger.reserve_inc_xrp

console.log(`Base reserve: ${baseReserve} XRP`)
console.log(`Incremental reserve: ${reserveInc} XRP`)

// Look up owner count ----------------------

const address = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh" // replace with any address
const accountInfo = await client.request({ command: "account_info", account: address })
const ownerCount = accountInfo.result.account_data.OwnerCount

// Calculate total reserve ----------------------

const totalReserve = baseReserve + (ownerCount * reserveInc)

console.log(`Owner count: ${ownerCount}`)
console.log(`Total reserve: ${totalReserve} XRP`)

await client.disconnect()