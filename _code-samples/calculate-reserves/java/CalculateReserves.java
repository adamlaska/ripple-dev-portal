
// Set up client ----------------------

import okhttp3.HttpUrl;
import org.xrpl.xrpl4j.client.JsonRpcClientErrorException;
import org.xrpl.xrpl4j.client.XrplClient;
import org.xrpl.xrpl4j.model.client.accounts.AccountInfoRequestParams;
import org.xrpl.xrpl4j.model.client.common.LedgerSpecifier;
import org.xrpl.xrpl4j.model.transactions.Address;
import java.math.BigDecimal;

public class CalculateReserves {
    public static void main(String[] args) throws JsonRpcClientErrorException {
        HttpUrl rippledUrl = HttpUrl.get("https://s.devnet.rippletest.net:51234/");
        XrplClient xrplClient = new XrplClient(rippledUrl);

// Look up reserve values ----------------------

        var serverInfo = xrplClient.serverInformation();
        var validatedLedger = serverInfo.info().validatedLedger().get();

        BigDecimal baseReserve = validatedLedger.reserveBaseXrp().toXrp();
        BigDecimal reserveInc  = validatedLedger.reserveIncXrp().toXrp();

        System.out.println("Base reserve: " + baseReserve + " XRP");
        System.out.println("Incremental reserve: " + reserveInc + " XRP");

// Look up owner count ----------------------

        Address address = Address.of("rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh");
        var accountInfo = xrplClient.accountInfo(
            AccountInfoRequestParams.builder()
                .account(address)
                .ledgerSpecifier(LedgerSpecifier.VALIDATED)
                .build()
        );

        long ownerCount = accountInfo.accountData().ownerCount().longValue();

// Calculate total reserve ----------------------

        BigDecimal totalReserve = baseReserve.add(reserveInc.multiply(BigDecimal.valueOf(ownerCount)));

        System.out.println("Owner count: " + ownerCount);
        System.out.println("Total reserve: " + totalReserve + " XRP");
    }
}
