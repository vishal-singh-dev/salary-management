import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { getSalaryAnalytics, listMasterData } from "@/lib/api";
import { DashboardClient } from "@/app/dashboard/DashboardClient";
import type { MasterData, SalaryAnalyticsResponse } from "@/lib/types";

vi.mock("@/lib/api", () => ({
  getSalaryAnalytics: vi.fn(),
  listMasterData: vi.fn(),
}));

const analyticsResponse: SalaryAnalyticsResponse = {
  filters: {
    country_code: "IN",
    department: "Engineering",
    title: null,
    include_inactive: false,
    currency_basis: "local",
  },
  employee_count: 42,
  currency_code: "INR",
  min_base_salary: "500000",
  max_base_salary: "2500000",
  mean_base_salary: "1250000",
  median_base_salary: "1100000",
  mode_base_salary: "1000000",
};

const masterDataResponse: MasterData[] = [
  { category: "country", description: "INDIA", value: "IN" },
  { category: "country", description: "GERMANY", value: "DE" },
  { category: "department", description: "Engineering", value: "ENG" },
  { category: "department", description: "Finance", value: "FIN" },
  { category: "job_title", description: "Software Engineer", value: "SWE" },
  { category: "job_title", description: "Senior Software Engineer", value: "SR_SWE" },
];

describe("DashboardClient", () => {
  beforeEach(() => {
    vi.mocked(listMasterData).mockResolvedValue(masterDataResponse);
    vi.mocked(getSalaryAnalytics).mockResolvedValue(analyticsResponse);
  });

  it("renders salary metrics from the analytics endpoint", async () => {
    render(<DashboardClient />);

    expect(screen.getByText("Loading salary insights...")).toBeInTheDocument();

    expect(await screen.findByText("Employees")).toBeInTheDocument();
    expect(screen.getByText("42")).toBeInTheDocument();
    expect(screen.getByText("Salary distribution")).toBeInTheDocument();
    expect(screen.getByText("Mean")).toBeInTheDocument();
  });

  it("applies dashboard filters", async () => {
    const user = userEvent.setup();
    render(<DashboardClient />);

    await screen.findByText("Employees");
    await user.selectOptions(screen.getByLabelText("Department"), "FIN");
    await user.selectOptions(screen.getByLabelText("Job title"), "SWE");
    await user.click(screen.getByRole("button", { name: "Apply filters" }));

    await waitFor(() => {
      expect(getSalaryAnalytics).toHaveBeenLastCalledWith(
        expect.objectContaining({ department: "FIN", title: "SWE" }),
      );
    });
  });
});
