import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  getUserLoans,
  getPendingLoans,
  updateLoanStatus,
  repayLoan,
  applyForLoan,
} from "../../api/loanClient";

import { fetchWithAuth } from "../../api/apiClient";

vi.mock("../../api/apiClient", () => ({
  fetchWithAuth: vi.fn(),
}));

const mockedFetchWithAuth = vi.mocked(fetchWithAuth);

describe("loanClient", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("getUserLoans", () => {
    it("returns the user's loans", async () => {
      const response = {
        loans: [
          {
            id: 1,
            loan_type: "House",
            loan_amount: 100000,
            duration: 120,
            current_loan_status: "ACCEPTED",
            interest: 5,
            emi: 1060.66,
          },
        ],
      };

      mockedFetchWithAuth.mockResolvedValue(
        new Response(JSON.stringify(response), {
          status: 200,
        }),
      );

      const result = await getUserLoans();

      expect(result).toEqual(response);

      expect(mockedFetchWithAuth).toHaveBeenCalledWith(
        expect.stringContaining("/loans/my-loans"),
      );
    });

    it("throws the API error message when the request fails", async () => {
      mockedFetchWithAuth.mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: "Unable to retrieve loans.",
          }),
          {
            status: 500,
          },
        ),
      );

      await expect(getUserLoans()).rejects.toThrow("Unable to retrieve loans.");
    });

    it("throws the default error when no detail is provided", async () => {
      mockedFetchWithAuth.mockResolvedValue(
        new Response(JSON.stringify({}), {
          status: 500,
        }),
      );

      await expect(getUserLoans()).rejects.toThrow("Failed to load loans.");
    });
  });

  describe("getPendingLoans", () => {
    it("returns pending loans", async () => {
      const response = {
        loans: [
          {
            id: 10,
            loan_type: "Automobile",
            loan_amount: 20000,
            duration: 60,
            current_loan_status: "PENDING",
            interest: 6,
            emi: 386.66,
          },
        ],
      };

      mockedFetchWithAuth.mockResolvedValue(
        new Response(JSON.stringify(response), {
          status: 200,
        }),
      );

      const result = await getPendingLoans();

      expect(result).toEqual(response);

      expect(mockedFetchWithAuth).toHaveBeenCalledWith(
        expect.stringContaining("/loans/pending"),
      );
    });

    it("returns an empty loan list", async () => {
      const response = {
        loans: [],
      };

      mockedFetchWithAuth.mockResolvedValue(
        new Response(JSON.stringify(response), {
          status: 200,
        }),
      );

      const result = await getPendingLoans();

      expect(result).toEqual({
        loans: [],
      });
    });

    it("throws the API error message when the request fails", async () => {
      mockedFetchWithAuth.mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: "Failed to retrieve pending loans.",
          }),
          {
            status: 403,
          },
        ),
      );

      await expect(getPendingLoans()).rejects.toThrow(
        "Failed to retrieve pending loans.",
      );
    });

    it("throws the default error when no detail is provided", async () => {
      mockedFetchWithAuth.mockResolvedValue(
        new Response(JSON.stringify({}), {
          status: 500,
        }),
      );

      await expect(getPendingLoans()).rejects.toThrow(
        "Failed to load pending loans.",
      );
    });
  });

  describe("updateLoanStatus", () => {
    it("accepts a loan", async () => {
      const response = {
        eligible: true,
        status: "ACCEPTED",
        loan_id: 1,
      };

      mockedFetchWithAuth.mockResolvedValue(
        new Response(JSON.stringify(response), {
          status: 200,
        }),
      );

      const result = await updateLoanStatus(1, "ACCEPTED");

      expect(result).toEqual(response);

      expect(mockedFetchWithAuth).toHaveBeenCalledWith(
        expect.stringContaining("/loans/1/decision"),
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            status: "ACCEPTED",
          }),
        },
      );
    });

    it("rejects a loan", async () => {
      const response = {
        eligible: true,
        status: "REJECTED",
        loan_id: 5,
      };

      mockedFetchWithAuth.mockResolvedValue(
        new Response(JSON.stringify(response), {
          status: 200,
        }),
      );

      const result = await updateLoanStatus(5, "REJECTED");

      expect(result).toEqual(response);

      expect(mockedFetchWithAuth).toHaveBeenCalledWith(
        expect.stringContaining("/loans/5/decision"),
        expect.objectContaining({
          method: "PATCH",
          body: JSON.stringify({
            status: "REJECTED",
          }),
        }),
      );
    });

    it("throws the API error message when the request fails", async () => {
      mockedFetchWithAuth.mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: "Loan cannot be updated.",
          }),
          {
            status: 400,
          },
        ),
      );

      await expect(updateLoanStatus(1, "ACCEPTED")).rejects.toThrow(
        "Loan cannot be updated.",
      );
    });

    it("throws the default error when no detail is provided", async () => {
      mockedFetchWithAuth.mockResolvedValue(
        new Response(JSON.stringify({}), {
          status: 500,
        }),
      );

      await expect(updateLoanStatus(1, "ACCEPTED")).rejects.toThrow(
        "Failed to update loan status.",
      );
    });
  });

  describe("repayLoan", () => {
    it("submits a loan repayment", async () => {
      const request = {
        loan_id: 10,
        amount: 500,
      };

      const response = {
        loan_id: 10,
        repayment_amount: 500,
        remaining_amount: 9500,
        status: "ACCEPTED",
      };

      mockedFetchWithAuth.mockResolvedValue(
        new Response(JSON.stringify(response), {
          status: 200,
        }),
      );

      const result = await repayLoan(request);

      expect(result).toEqual(response);

      expect(mockedFetchWithAuth).toHaveBeenCalledWith(
        expect.stringContaining("/loans/repay"),
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(request),
        },
      );
    });

    it("throws the API error message when repayment fails", async () => {
      mockedFetchWithAuth.mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: "Insufficient funds.",
          }),
          {
            status: 400,
          },
        ),
      );

      await expect(
        repayLoan({
          loan_id: 10,
          amount: 500,
        }),
      ).rejects.toThrow("Insufficient funds.");
    });

    it("throws the default error when no detail is provided", async () => {
      mockedFetchWithAuth.mockResolvedValue(
        new Response(JSON.stringify({}), {
          status: 500,
        }),
      );

      await expect(
        repayLoan({
          loan_id: 10,
          amount: 500,
        }),
      ).rejects.toThrow("Failed to make loan repayment.");
    });
  });

  describe("applyForLoan", () => {
    it("submits a loan application", async () => {
      const request = {
        loan_type: "House",
        loan_amount: 100000,
        monthly_income: 5000,
        monthly_expenses: 2000,
        duration: 120,
      };

      const response = {
        eligible: true,
        status: "PENDING",
        loan_id: 15,
      };

      mockedFetchWithAuth.mockResolvedValue(
        new Response(JSON.stringify(response), {
          status: 200,
        }),
      );

      const result = await applyForLoan(request);

      expect(result).toEqual(response);

      expect(mockedFetchWithAuth).toHaveBeenCalledWith(
        expect.stringContaining("/loans/loanForm"),
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(request),
        },
      );
    });

    it("returns a rejected application", async () => {
      const request = {
        loan_type: "Emergency Expense",
        loan_amount: 50000,
        monthly_income: 2000,
        monthly_expenses: 1900,
        duration: 12,
      };

      const response = {
        eligible: false,
        status: "REJECTED",
        loan_id: null,
      };

      mockedFetchWithAuth.mockResolvedValue(
        new Response(JSON.stringify(response), {
          status: 200,
        }),
      );

      const result = await applyForLoan(request);

      expect(result).toEqual(response);
      expect(result.eligible).toBe(false);
      expect(result.loan_id).toBeNull();
    });

    it("throws the API error message when application fails", async () => {
      mockedFetchWithAuth.mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: "Invalid loan application.",
          }),
          {
            status: 400,
          },
        ),
      );

      await expect(
        applyForLoan({
          loan_type: "House",
          loan_amount: 100000,
          monthly_income: 5000,
          monthly_expenses: 2000,
          duration: 120,
        }),
      ).rejects.toThrow("Invalid loan application.");
    });

    it("throws the default error when no detail is provided", async () => {
      mockedFetchWithAuth.mockResolvedValue(
        new Response(JSON.stringify({}), {
          status: 500,
        }),
      );

      await expect(
        applyForLoan({
          loan_type: "House",
          loan_amount: 100000,
          monthly_income: 5000,
          monthly_expenses: 2000,
          duration: 120,
        }),
      ).rejects.toThrow("Failed to submit loan application.");
    });
  });
});
