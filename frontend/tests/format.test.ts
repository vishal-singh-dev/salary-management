import { describe, expect, it } from "vitest";

import { formatMoney, meanMedianDifference, salaryRange } from "@/lib/format";

describe("format helpers", () => {
  it("formats money with a currency code", () => {
    expect(formatMoney("120000", "USD")).toBe("$120,000");
  });

  it("returns a salary range when min and max exist", () => {
    expect(salaryRange("100", "250")).toBe("150");
  });

  it("returns mean median difference", () => {
    expect(meanMedianDifference("200", "150")).toBe("50");
  });

  it("handles missing salary values", () => {
    expect(formatMoney(null, "USD")).toBe("Not available");
    expect(salaryRange(null, "250")).toBeNull();
  });
});
