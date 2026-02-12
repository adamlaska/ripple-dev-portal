# Lending Protocol Examples (Python)

This directory contains Python examples demonstrating how to create a loan broker, claw back first-loss capital, deposit and withdraw first-loss capital, create a loan, manage a loan, and repay a loan.

## Setup

Install dependencies before running any examples:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Create a Loan Broker

```sh
python3 create_loan_broker.py
```

The script should output the LoanBrokerSet transaction, loan broker ID, and loan broker pseudo-account:

```sh
Loan broker/vault owner address: rBeEX3qQzP3UL5WMwZAzdPPpzckH73YvBn
Vault ID: 2B71E8E1323BFC8F2AC27F8C217870B63921EFA0C02DF7BA8B099C7DC6A1D00F

=== Preparing LoanBrokerSet transaction ===

{
  "Account": "rBeEX3qQzP3UL5WMwZAzdPPpzckH73YvBn",
  "TransactionType": "LoanBrokerSet",
  "SigningPubKey": "",
  "VaultID": "2B71E8E1323BFC8F2AC27F8C217870B63921EFA0C02DF7BA8B099C7DC6A1D00F",
  "ManagementFeeRate": 1000
}

=== Submitting LoanBrokerSet transaction ===

Loan broker created successfully!

=== Loan Broker Information ===

LoanBroker ID: 86911896026EA9DEAEFC1A7959BC05D8B1A1EC25B9960E8C54424B7DC41F8DA8
LoanBroker Psuedo-Account Address: rPhpC2XGz7v5g2rPom7JSWJcic1cnkoBh9
```

---

## Claw Back First-loss Capital

```sh
python3 cover_clawback.py
```

The script should output the cover available, the LoanBrokerCoverDeposit transaction, cover available after the deposit, the LoanBrokerCoverClawback transaction, and the final cover available after the clawback:

```sh
Loan broker address: rBeEX3qQzP3UL5WMwZAzdPPpzckH73YvBn
MPT issuer address: rNzJg2EVwo56eAoBxz5WnTfmgoLbfaAT8d
LoanBrokerID: 041E256F124841FF81DF105C62A72676BFD746975F86786166B689F304BE96E0
MPT ID: 0037A8ED99701AFEC4BCC3A39299252CA41838059572E7F2

=== Cover Available ===

1000 TSTUSD

=== Preparing LoanBrokerCoverDeposit transaction ===

{
  "Account": "rBeEX3qQzP3UL5WMwZAzdPPpzckH73YvBn",
  "TransactionType": "LoanBrokerCoverDeposit",
  "SigningPubKey": "",
  "LoanBrokerID": "041E256F124841FF81DF105C62A72676BFD746975F86786166B689F304BE96E0",
  "Amount": {
    "mpt_issuance_id": "0037A8ED99701AFEC4BCC3A39299252CA41838059572E7F2",
    "value": "1000"
  }
}

=== Submitting LoanBrokerCoverDeposit transaction ===

Cover deposit successful!

=== Cover Available After Deposit ===

2000 TSTUSD

=== Verifying Asset Issuer ===

MPT issuer account verified: rNzJg2EVwo56eAoBxz5WnTfmgoLbfaAT8d. Proceeding to clawback.

=== Preparing LoanBrokerCoverClawback transaction ===

{
  "Account": "rNzJg2EVwo56eAoBxz5WnTfmgoLbfaAT8d",
  "TransactionType": "LoanBrokerCoverClawback",
  "SigningPubKey": "",
  "LoanBrokerID": "041E256F124841FF81DF105C62A72676BFD746975F86786166B689F304BE96E0",
  "Amount": {
    "mpt_issuance_id": "0037A8ED99701AFEC4BCC3A39299252CA41838059572E7F2",
    "value": "2000"
  }
}

=== Submitting LoanBrokerCoverClawback transaction ===

Successfully clawed back 2000 TSTUSD!

=== Final Cover Available After Clawback ===

0 TSTUSD
```

---

## Deposit and Withdraw First-loss Capital

```sh
python3 cover_deposit_and_withdraw.py
```

The script should output the LoanBrokerCoverDeposit, cover balance after the deposit, the LoanBrokerCoverWithdraw transaction, and the cover balance after the withdrawal:

```sh
Loan broker address: rBeEX3qQzP3UL5WMwZAzdPPpzckH73YvBn
LoanBrokerID: 041E256F124841FF81DF105C62A72676BFD746975F86786166B689F304BE96E0
MPT ID: 0037A8ED99701AFEC4BCC3A39299252CA41838059572E7F2

=== Preparing LoanBrokerCoverDeposit transaction ===

{
  "Account": "rBeEX3qQzP3UL5WMwZAzdPPpzckH73YvBn",
  "TransactionType": "LoanBrokerCoverDeposit",
  "SigningPubKey": "",
  "LoanBrokerID": "041E256F124841FF81DF105C62A72676BFD746975F86786166B689F304BE96E0",
  "Amount": {
    "mpt_issuance_id": "0037A8ED99701AFEC4BCC3A39299252CA41838059572E7F2",
    "value": "2000"
  }
}

=== Submitting LoanBrokerCoverDeposit transaction ===

Cover deposit successful!

=== Cover Balance ===

LoanBroker Pseudo-Account: rUrs1bkhQyh1nxE7u99H92U2Tg8Pogw1bZ
Cover balance after deposit: 2000 TSTUSD

=== Preparing LoanBrokerCoverWithdraw transaction ===

{
  "Account": "rBeEX3qQzP3UL5WMwZAzdPPpzckH73YvBn",
  "TransactionType": "LoanBrokerCoverWithdraw",
  "SigningPubKey": "",
  "LoanBrokerID": "041E256F124841FF81DF105C62A72676BFD746975F86786166B689F304BE96E0",
  "Amount": {
    "mpt_issuance_id": "0037A8ED99701AFEC4BCC3A39299252CA41838059572E7F2",
    "value": "1000"
  }
}

=== Submitting LoanBrokerCoverWithdraw transaction ===

Cover withdraw successful!

=== Updated Cover Balance ===

LoanBroker Pseudo-Account: rUrs1bkhQyh1nxE7u99H92U2Tg8Pogw1bZ
Cover balance after withdraw: 1000 TSTUSD
```

---

## Create a Loan

```sh
python3 create_loan.py
```

The script should output the LoanSet transaction, the updated LoanSet transaction with the loan broker signature, the final LoanSet transaction with the borrower signature added, and then the loan information:

```sh
Loan broker address: rBeEX3qQzP3UL5WMwZAzdPPpzckH73YvBn
Borrower address: rKDcZNbMCh8XsKE61qDw6XJnWNg2nqQB1u
LoanBrokerID: 041E256F124841FF81DF105C62A72676BFD746975F86786166B689F304BE96E0

=== Preparing LoanSet transaction ===

{
  "Account": "rBeEX3qQzP3UL5WMwZAzdPPpzckH73YvBn",
  "TransactionType": "LoanSet",
  "Fee": "2",
  "Sequence": 3647738,
  "LastLedgerSequence": 3650147,
  "SigningPubKey": "",
  "LoanBrokerID": "041E256F124841FF81DF105C62A72676BFD746975F86786166B689F304BE96E0",
  "Counterparty": "rKDcZNbMCh8XsKE61qDw6XJnWNg2nqQB1u",
  "LoanOriginationFee": "100",
  "LoanServiceFee": "10",
  "InterestRate": 500,
  "PrincipalRequested": "1000",
  "PaymentTotal": 12,
  "PaymentInterval": 2592000,
  "GracePeriod": 604800
}

=== Adding loan broker signature ===

TxnSignature: C702BCB348B2813329C31823B1BA2E03F7CDFAF7564A68918450120A252A748527A7F73764FC7F5576F604C844941646128117406E5ACB3986B873B43EAD1B08
SigningPubKey: ED6AAF195E55535311CA163BDA6722A1452829F10C3FD73B620D8FCDB5C5CBE04B

Signed loan_set_tx for borrower to sign over:
{
  "Account": "rBeEX3qQzP3UL5WMwZAzdPPpzckH73YvBn",
  "Counterparty": "rKDcZNbMCh8XsKE61qDw6XJnWNg2nqQB1u",
  "Fee": "2",
  "GracePeriod": 604800,
  "InterestRate": 500,
  "LastLedgerSequence": 3650147,
  "LoanBrokerID": "041E256F124841FF81DF105C62A72676BFD746975F86786166B689F304BE96E0",
  "LoanOriginationFee": "100",
  "LoanServiceFee": "10",
  "PaymentInterval": 2592000,
  "PaymentTotal": 12,
  "PrincipalRequested": "1000",
  "Sequence": 3647738,
  "SigningPubKey": "ED6AAF195E55535311CA163BDA6722A1452829F10C3FD73B620D8FCDB5C5CBE04B",
  "TransactionType": "LoanSet",
  "TxnSignature": "C702BCB348B2813329C31823B1BA2E03F7CDFAF7564A68918450120A252A748527A7F73764FC7F5576F604C844941646128117406E5ACB3986B873B43EAD1B08"
}

=== Adding borrower signature ===

Borrower TxnSignature: AD69C2264F8B9CDA95AE49E411F31676EC7F53993A75C9ED797CB0497829303AD44C59DFD6174309B31C7686C87BDE102640B9D6CF6CDDE4E4BF909362CC6500
Borrower SigningPubKey: ED02C92B1701E364C2C6E4FD983109A4CAAD755F840C5BAB5EB2247511D34699A2

Fully signed LoanSet transaction:
{
  "Account": "rBeEX3qQzP3UL5WMwZAzdPPpzckH73YvBn",
  "Counterparty": "rKDcZNbMCh8XsKE61qDw6XJnWNg2nqQB1u",
  "CounterpartySignature": {
    "SigningPubKey": "ED02C92B1701E364C2C6E4FD983109A4CAAD755F840C5BAB5EB2247511D34699A2",
    "TxnSignature": "AD69C2264F8B9CDA95AE49E411F31676EC7F53993A75C9ED797CB0497829303AD44C59DFD6174309B31C7686C87BDE102640B9D6CF6CDDE4E4BF909362CC6500"
  },
  "Fee": "2",
  "GracePeriod": 604800,
  "InterestRate": 500,
  "LastLedgerSequence": 3650147,
  "LoanBrokerID": "041E256F124841FF81DF105C62A72676BFD746975F86786166B689F304BE96E0",
  "LoanOriginationFee": "100",
  "LoanServiceFee": "10",
  "PaymentInterval": 2592000,
  "PaymentTotal": 12,
  "PrincipalRequested": "1000",
  "Sequence": 3647738,
  "SigningPubKey": "ED6AAF195E55535311CA163BDA6722A1452829F10C3FD73B620D8FCDB5C5CBE04B",
  "TransactionType": "LoanSet",
  "TxnSignature": "C702BCB348B2813329C31823B1BA2E03F7CDFAF7564A68918450120A252A748527A7F73764FC7F5576F604C844941646128117406E5ACB3986B873B43EAD1B08"
}

=== Submitting signed LoanSet transaction ===

Loan created successfully!

=== Loan Information ===

{
  "Borrower": "rKDcZNbMCh8XsKE61qDw6XJnWNg2nqQB1u",
  "GracePeriod": 604800,
  "InterestRate": 500,
  "LoanBrokerID": "041E256F124841FF81DF105C62A72676BFD746975F86786166B689F304BE96E0",
  "LoanOriginationFee": "100",
  "LoanSequence": 3,
  "LoanServiceFee": "10",
  "NextPaymentDueDate": 826789401,
  "PaymentInterval": 2592000,
  "PaymentRemaining": 12,
  "PeriodicPayment": "83.55610375293148956",
  "PrincipalOutstanding": "1000",
  "StartDate": 824197401,
  "TotalValueOutstanding": "1003"
}
```

---

## Manage a Loan

```sh
python3 loan_manage.py
```

The script should output the initial status of the loan, the LoanManage transaction, and the updated loan status and grace period after impairment. The script will countdown the grace period before outputting another LoanManage transaction, and then the final flags on the loan.

```sh
Loan broker address: r9x3etrs2GZSF73vQ8endi9CWpKr5N2Rjn
LoanID: E86DB385401D361A33DD74C8E1B44D7F996E9BA02724BCD44127F60BE057A322

=== Loan Status ===

Total Amount Owed: 1001 TSTUSD.
Payment Due Date: 2026-03-14 02:01:51

=== Preparing LoanManage transaction to impair loan ===

{
  "Account": "r9x3etrs2GZSF73vQ8endi9CWpKr5N2Rjn",
  "TransactionType": "LoanManage",
  "Flags": 131072,
  "SigningPubKey": "",
  "LoanID": "E86DB385401D361A33DD74C8E1B44D7F996E9BA02724BCD44127F60BE057A322"
}

=== Submitting LoanManage impairment transaction ===

Loan impaired successfully!
New Payment Due Date: 2026-02-12 01:01:50
Grace Period: 60 seconds

=== Countdown until loan can be defaulted ===

Grace period expired. Loan can now be defaulted.

=== Preparing LoanManage transaction to default loan ===

{
  "Account": "r9x3etrs2GZSF73vQ8endi9CWpKr5N2Rjn",
  "TransactionType": "LoanManage",
  "Flags": 65536,
  "SigningPubKey": "",
  "LoanID": "E86DB385401D361A33DD74C8E1B44D7F996E9BA02724BCD44127F60BE057A322"
}

=== Submitting LoanManage default transaction ===

Loan defaulted successfully!

=== Checking final loan status ===

Final loan flags: ['TF_LOAN_DEFAULT', 'TF_LOAN_IMPAIR']
```

## Pay a Loan

```sh
node loanPay.js
```

The script should output the amount required to totally pay off a loan, the LoanPay transaction, the amount due after the payment, the LoanDelete transaction, and then the status of the loan ledger entry:

```sh
Borrower address: r46Ef5jjnaY7CDP7g22sQgSJJPQEBSmbWA
LoanID: 8AC2B4425E604E7BB1082DD2BF2CA902B5087143B7775BE0A4DA954D3F52D06E
MPT ID: 0031034FF84EB2E8348A34F0A8889A54F45F180E80F12341

=== Loan Status ===

Amount Owed: 1001 TSTUSD
Loan Service Fee: 10 TSTUSD
Total Payment Due (including fees): 1011 TSTUSD

=== Preparing LoanPay transaction ===

{
  "TransactionType": "LoanPay",
  "Account": "r46Ef5jjnaY7CDP7g22sQgSJJPQEBSmbWA",
  "LoanID": "8AC2B4425E604E7BB1082DD2BF2CA902B5087143B7775BE0A4DA954D3F52D06E",
  "Amount": {
    "mpt_issuance_id": "0031034FF84EB2E8348A34F0A8889A54F45F180E80F12341",
    "value": "1011"
  }
}

=== Submitting LoanPay transaction ===

Loan paid successfully!

=== Loan Status After Payment ===

Outstanding Loan Balance: Loan fully paid off!

=== Preparing LoanDelete transaction ===

{
  "TransactionType": "LoanDelete",
  "Account": "r46Ef5jjnaY7CDP7g22sQgSJJPQEBSmbWA",
  "LoanID": "8AC2B4425E604E7BB1082DD2BF2CA902B5087143B7775BE0A4DA954D3F52D06E"
}

=== Submitting LoanDelete transaction ===

Loan deleted successfully!

=== Verifying Loan Deletion ===

Loan has been successfully removed from the XRP Ledger!
```
