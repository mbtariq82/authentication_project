import { describe, expect, it } from "vitest";

import { buildDateOfBirth } from "./dateOfBirth";

const today = new Date(2026, 7, 20);

describe("buildDateOfBirth", () => {
  it("allows the optional date to remain empty", () => {
    expect(buildDateOfBirth("", "", "", today)).toEqual({ isValid: true });
  });

  it("formats a directly entered year as an ISO date", () => {
    expect(buildDateOfBirth("9", "11", "1999", today)).toEqual({
      isValid: true,
      value: "1999-11-09",
    });
  });

  it("rejects impossible calendar dates", () => {
    expect(buildDateOfBirth("29", "2", "2023", today)).toEqual({
      isValid: false,
    });
  });

  it("rejects dates in the future", () => {
    expect(buildDateOfBirth("21", "8", "2026", today)).toEqual({
      isValid: false,
    });
  });
});
