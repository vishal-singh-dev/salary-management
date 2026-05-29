import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  ApiError,
  buildUrl,
  getHealth,
  getNextEmployeeId,
  getSalaryAnalytics,
  listEmployees,
  listMasterData,
} from "@/lib/api";

describe("api client", () => {
  beforeEach(() => {
    process.env.NEXT_PUBLIC_API_BASE_URL = "https://api.example.com";
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    delete process.env.NEXT_PUBLIC_API_BASE_URL;
  });

  it("builds backend urls with query parameters", () => {
    expect(buildUrl("/api/v1/employees", { limit: 25, offset: 0 })).toBe(
      "https://api.example.com/api/v1/employees?limit=25&offset=0",
    );
  });

  it("calls the health endpoint for smoke checks", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ status: "ok", environment: "production" }), { status: 200 }),
    );

    await expect(getHealth()).resolves.toEqual({ status: "ok", environment: "production" });
    expect(fetch).toHaveBeenCalledWith("https://api.example.com/health", expect.any(Object));
  });

  it("passes employee pagination and active filters", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ items: [], total: 0, limit: 25, offset: 0 }), { status: 200 }),
    );

    await listEmployees({ limit: 25, offset: 0, includeInactive: false });

    expect(fetch).toHaveBeenCalledWith(
      "https://api.example.com/api/v1/employees?limit=25&offset=0&include_inactive=false",
      expect.any(Object),
    );
  });

  it("requests the next employee id", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ employee_id: "EMP-000011" }), { status: 200 }),
    );

    await expect(getNextEmployeeId()).resolves.toEqual({ employee_id: "EMP-000011" });
    expect(fetch).toHaveBeenCalledWith(
      "https://api.example.com/api/v1/employees/next-id",
      expect.any(Object),
    );
  });

  it("calls master data endpoint with category filters", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify([{ category: "department", description: "Engineering", value: "ENG" }]),
        { status: 200 },
      ),
    );

    await listMasterData("department");

    expect(fetch).toHaveBeenCalledWith(
      "https://api.example.com/api/v1/master-data?category=department",
      expect.any(Object),
    );
  });

  it("passes salary analytics filters", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          filters: {
            country_code: "IN",
            department: "Engineering",
            title: null,
            include_inactive: false,
            currency_basis: "local",
          },
          employee_count: 0,
          currency_code: null,
          min_base_salary: null,
          max_base_salary: null,
          mean_base_salary: null,
          median_base_salary: null,
          mode_base_salary: null,
        }),
        { status: 200 },
      ),
    );

    await getSalaryAnalytics({
      country_code: "IN",
      department: "Engineering",
      currency_basis: "local",
    });

    expect(fetch).toHaveBeenCalledWith(
      "https://api.example.com/api/v1/analytics/salaries?country_code=IN&department=Engineering&include_inactive=false&currency_basis=local",
      expect.any(Object),
    );
  });

  it("raises ApiError with backend detail when requests fail", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: "Employee not found" }), { status: 404 }),
    );

    await expect(getHealth()).rejects.toEqual(new ApiError("Employee not found", 404));
  });
});
