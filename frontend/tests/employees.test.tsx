import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { EmployeesClient } from "@/app/employees/EmployeesClient";
import { listEmployees } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  listEmployees: vi.fn(),
}));

describe("EmployeesClient", () => {
  beforeEach(() => {
    vi.mocked(listEmployees).mockResolvedValue({
      items: [
        {
          id: "employee-uuid",
          employee_id: "EMP-000001",
          full_name: "Asha Patel",
          title: "HR Manager",
          department: "Human Resources",
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
  });

  it("renders employee rows from the API", async () => {
    render(<EmployeesClient />);

    expect(await screen.findByText("Asha Patel")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "EMP-000001" })).toHaveAttribute(
      "href",
      "/employees/employee-uuid",
    );
    expect(screen.getByText("Human Resources")).toBeInTheDocument();
  });
});
