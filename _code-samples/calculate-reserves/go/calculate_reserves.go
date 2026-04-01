
// Set up client ----------------------
package main

import (
	"fmt"
	"github.com/Peersyst/xrpl-go/xrpl/queries/account"
	"github.com/Peersyst/xrpl-go/xrpl/queries/server"
	"github.com/Peersyst/xrpl-go/xrpl/transaction/types"
	"github.com/Peersyst/xrpl-go/xrpl/websocket"
)

func main() {
	client := websocket.NewClient(
		websocket.NewClientConfig().
			WithHost("wss://s.devnet.rippletest.net:51233"),
	)
	defer client.Disconnect()

	if err := client.Connect(); err != nil {
		panic(err)
	}

// Look up reserve values ----------------------

	res, err := client.Request(&server.InfoRequest{})
	if err != nil {
		panic(err)
	}
	var serverInfo server.InfoResponse
	if err := res.GetResult(&serverInfo); err != nil {
		panic(err)
	}

	baseReserve := serverInfo.Info.ValidatedLedger.ReserveBaseXRP
	reserveInc := serverInfo.Info.ValidatedLedger.ReserveIncXRP

	fmt.Printf("Base reserve: %v XRP\n", baseReserve)
	fmt.Printf("Incremental reserve: %v XRP\n", reserveInc)

// Look up owner count ----------------------

	address := types.Address("rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")
	accountInfo, err := client.GetAccountInfo(&account.InfoRequest{Account: address})
	if err != nil {
		panic(err)
	}

	ownerCount := accountInfo.AccountData.OwnerCount

// Calculate total reserve ----------------------

	totalReserve := float64(baseReserve) + (float64(ownerCount) * float64(reserveInc))

	fmt.Printf("Owner count: %v\n", ownerCount)
	fmt.Printf("Total reserve: %v XRP\n", totalReserve)
}