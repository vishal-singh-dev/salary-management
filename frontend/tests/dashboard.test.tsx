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
    department: "HR",
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
  master("Country", "India", "IN", null, null, 1),
  master("Country", "Germany", "DE", null, null, 2),
  master("Department", "HR", "HR", "Country", "IN", 1),
  master("Department", "Finance", "FIN", "Country", "IN", 2),
  master("JobTitle", "HR Finance", "HRF", "Department", "HR", 1),
  master("JobTitle", "Finance Manager", "FIN_MGR", "Department", "FIN", 2),
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
    await user.selectOptions(screen.getByLabelText("Job title"), "FIN_MGR");
    await user.click(screen.getByRole("button", { name: "Apply filters" }));

    await waitFor(() => {
      expect(getSalaryAnalytics).toHaveBeenLastCalledWith(
        expect.objectContaining({ department: "FIN", title: "FIN_MGR" }),
      );
    });
  });
});

function master(
  category_name: MasterData["category_name"],
  display_name: string,
  code: string,
  parent_category_name: string | null,
  parent_code: string | null,
  sort_order: number,
): MasterData {
  return {
    category_name,
    display_name,
    code,
    parent_category_name,
    parent_code,
    sort_order,
    is_active: true,
  };
}
