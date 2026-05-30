import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { EmployeesClient } from "@/app/employees/EmployeesClient";
import { listEmployees, listMasterData } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  listEmployees: vi.fn(),
  listMasterData: vi.fn(),
}));

describe("EmployeesClient", () => {
  beforeEach(() => {
    vi.mocked(listEmployees).mockResolvedValue({
      items: [
        {
          id: "employee-uuid",
          employee_id: "EMP-000001",
          first_name: "Asha",
          last_name: "Patel",
          gender: "Female",
          title: "HRF",
          department: "HR",
          country_code: "IN",
          from_date: "2026-01-01",
          to_date: null,
          created_at: "2026-05-29T00:00:00Z",
          current_salary: {
            id: "salary-uuid",
            employee_id: "employee-uuid",
            currency_code: "INR",
            base_amount: "2000000",
            variable_amount: "0",
            hra_allowance_amount: "0",
            pf_amount: "0",
            gratuity_amount: "0",
            effective_from: "2026-01-01",
            effective_to: null,
            exchange_rate_id: "fx-uuid",
            created_at: "2026-05-29T00:00:00Z",
          },
        },
      ],
      total: 1,
      limit: 25,
      offset: 0,
    });
    vi.mocked(listMasterData).mockResolvedValue([
      {
        category_name: "Department",
        display_name: "HR",
        code: "HR",
        parent_category_name: "Country",
        parent_code: "IN",
        sort_order: 1,
        is_active: true,
      },
      {
        category_name: "JobTitle",
        display_name: "HR Finance",
        code: "HRF",
        parent_category_name: "Department",
        parent_code: "HR",
        sort_order: 1,
        is_active: true,
      },
      {
        category_name: "Country",
        display_name: "India",
        code: "IN",
        parent_category_name: null,
        parent_code: null,
        sort_order: 1,
        is_active: true,
      },
    ]);
  });

  it("renders employee rows from the API", async () => {
    render(<EmployeesClient />);

    expect(await screen.findByText("Asha Patel")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "EMP-000001" })).toHaveAttribute(
      "href",
      "/employees/employeedetails?id=employee-uuid",
    );
    expect(screen.getByText("HR")).toBeInTheDocument();
  });
});
