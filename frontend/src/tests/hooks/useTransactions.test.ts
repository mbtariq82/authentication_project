import { describe, expect, it } from "vitest";

import { transactionQueryKeys } from "../../hooks/useTransactions";

describe("transaction query keys", () => {
  it("keeps filters isolated between transaction lists", () => {
    const allTransactions = transactionQueryKeys.list({});
    const pendingTransfers = transactionQueryKeys.list({
      status: "PENDING",
      transaction_type: "TRANSFER",
    });

    expect(allTransactions).not.toEqual(pendingTransfers);
    expect(pendingTransfers).toEqual([
      "transactions",
      "list",
      { status: "PENDING", transaction_type: "TRANSFER" },
    ]);
  });

  it("separates transaction details from logs", () => {
    expect(transactionQueryKeys.detail(4)).toEqual([
      "transactions",
      "detail",
      4,
    ]);
    expect(transactionQueryKeys.logs(4)).toEqual(["transactions", "logs", 4]);
  });
});
