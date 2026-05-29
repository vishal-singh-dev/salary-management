"use client";

import { useEffect, useMemo, useState } from "react";

import { MetricCard } from "@/components/MetricCard";
import { getSalaryAnalytics, listMasterData } from "@/lib/api";
import { formatMoney, formatNumber } from "@/lib/format";
import type { CurrencyBasis, SalaryAnalyticsResponse } from "@/lib/types";
import type { MasterData } from "@/lib/types";

type Filters = {
  countryCode: string;
  department: string;
  title: string;
  currencyBasis: CurrencyBasis;
  includeInactive: boolean;
};

const defaultFilters: Filters = {
  countryCode: "IN",
  department: "",
  title: "",
  currencyBasis: "local",
  includeInactive: false,
};
const fallbackMasterData: MasterData[] = [
  { category: "country", description: "INDIA", value: "IN" },
  { category: "country", description: "UNITED STATES", value: "US" },
  { category: "country", description: "UNITED KINGDOM", value: "GB" },
  { category: "country", description: "GERMANY", value: "DE" },
  { category: "country", description: "CANADA", value: "CA" },
  { category: "country", description: "AUSTRALIA", value: "AU" },
  { category: "department", description: "Engineering", value: "ENG" },
  { category: "department", description: "Product", value: "PROD" },
  { category: "department", description: "Data", value: "DATA" },
  { category: "department", description: "Human Resources", value: "HR" },
  { category: "department", description: "Finance", value: "FIN" },
  { category: "department", description: "Sales", value: "SALES" },
  { category: "department", description: "Support", value: "SUPPORT" },
  { category: "job_title", description: "Software Engineer", value: "SWE" },
  { category: "job_title", description: "Senior Software Engineer", value: "SR_SWE" },
  { category: "job_title", description: "Product Manager", value: "PM" },
  { category: "job_title", description: "Data Analyst", value: "DA" },
  { category: "job_title", description: "HR Business Partner", value: "HRBP" },
  { category: "job_title", description: "Finance Manager", value: "FIN_MGR" },
  { category: "job_title", description: "Sales Executive", value: "SALES_EXEC" },
  { category: "job_title", description: "Support Specialist", value: "SUPPORT_SPEC" },
];

export function DashboardClient() {
  const [draftFilters, setDraftFilters] = useState<Filters>(defaultFilters);
  const [appliedFilters, setAppliedFilters] = useState<Filters>(defaultFilters);
  const [masterData, setMasterData] = useState<MasterData[]>(fallbackMasterData);
  const [analytics, setAnalytics] = useState<SalaryAnalyticsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isMasterDataLoading, setIsMasterDataLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [masterDataError, setMasterDataError] = useState<string | null>(null);

  useEffect(() => {
    let isCurrent = true;

    async function loadMasterData() {
      setIsMasterDataLoading(true);
      setMasterDataError(null);
      try {
        const result = await listMasterData();
        if (isCurrent) {
          setMasterData(result);
        }
      } catch (caught) {
        if (isCurrent) {
          setMasterDataError(
            caught instanceof Error ? caught.message : "Unable to load dashboard filters",
          );
        }
      } finally {
        if (isCurrent) {
          setIsMasterDataLoading(false);
        }
      }
    }

    loadMasterData();

    return () => {
      isCurrent = false;
    };
  }, []);

  useEffect(() => {
    let isCurrent = true;

    async function loadAnalytics() {
      setIsLoading(true);
      setError(null);
      try {
        const result = await getSalaryAnalytics({
          country_code: appliedFilters.countryCode,
          department: appliedFilters.department,
          title: appliedFilters.title,
          currency_basis: appliedFilters.currencyBasis,
          include_inactive: appliedFilters.includeInactive,
        });
        if (isCurrent) {
          setAnalytics(result);
        }
      } catch (caught) {
        if (isCurrent) {
          setError(caught instanceof Error ? caught.message : "Unable to load salary analytics");
          setAnalytics(null);
        }
      } finally {
        if (isCurrent) {
          setIsLoading(false);
        }
      }
    }

    loadAnalytics();

    return () => {
      isCurrent = false;
    };
  }, [appliedFilters]);

  const currencyCode = analytics?.currency_code ?? (appliedFilters.currencyBasis === "usd" ? "USD" : null);
  const countryOptions = useMemo(() => optionsFor(masterData, "country"), [masterData]);
  const departmentOptions = useMemo(() => optionsFor(masterData, "department"), [masterData]);
  const titleOptions = useMemo(() => optionsFor(masterData, "job_title"), [masterData]);

  return (
    <>
      <section className="panel" aria-label="Dashboard filters">
        <div className="filter-grid">
          <div className="field">
            <label htmlFor="countryCode">Country</label>
            <select
              id="countryCode"
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  countryCode: event.target.value,
                }))
              }
              value={draftFilters.countryCode}
            >
              {countryOptions.length === 0 ? <option value="IN">INDIA</option> : null}
              {countryOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.description}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="department">Department</label>
            <select
              id="department"
              onChange={(event) =>
                setDraftFilters((current) => ({ ...current, department: event.target.value }))
              }
              value={draftFilters.department}
            >
              <option value="">Select department</option>
              {departmentOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.description}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="title">Job title</label>
            <select
              id="title"
              onChange={(event) =>
                setDraftFilters((current) => ({ ...current, title: event.target.value }))
              }
              value={draftFilters.title}
            >
              <option value="">Select job title</option>
              {titleOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.description}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="currencyBasis">Currency basis</label>
            <select
              id="currencyBasis"
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  currencyBasis: event.target.value as CurrencyBasis,
                }))
              }
              value={draftFilters.currencyBasis}
            >
              <option value="local">Local</option>
              <option value="usd">USD</option>
            </select>
          </div>
          <label className="checkbox-row">
            <input
              checked={draftFilters.includeInactive}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  includeInactive: event.target.checked,
                }))
              }
              type="checkbox"
            />
            Include inactive
          </label>
        </div>
        <div className="actions">
          <button
            className="button button-secondary"
            onClick={() => {
              setDraftFilters(defaultFilters);
              setAppliedFilters(defaultFilters);
            }}
            type="button"
          >
            Reset
          </button>
          <button
            className="button button-primary"
            onClick={() => setAppliedFilters(draftFilters)}
            type="button"
          >
            Apply filters
          </button>
        </div>
      </section>

      {isMasterDataLoading && masterData.length === 0 ? (
        <div className="status-message status-info">Loading dashboard filters...</div>
      ) : null}

      {masterDataError ? (
        <div className="status-message status-error">{masterDataError}</div>
      ) : null}

      {isLoading ? (
        <div className="status-message status-info">Loading salary insights...</div>
      ) : null}

      {error ? (
        <div className="status-message status-error">
          {error}
          <div className="section-gap">
            <button
              className="button button-secondary"
              onClick={() => setAppliedFilters({ ...appliedFilters })}
              type="button"
            >
              Retry
            </button>
          </div>
        </div>
      ) : null}

      {!isLoading && !error && analytics?.employee_count === 0 ? (
        <div className="status-message status-warning">
          No employees match the selected filters. Try a different country, department, or currency
          basis.
        </div>
      ) : null}

      {!isLoading && !error && analytics ? (
        <>
          <section className="metrics-grid metrics-grid-compact" aria-label="Salary metrics">
            <MetricCard label="Employees" value={formatNumber(analytics.employee_count)} />
            <MetricCard
              label="Minimum base salary"
              value={formatMoney(analytics.min_base_salary, currencyCode)}
            />
            <MetricCard
              label="Maximum base salary"
              value={formatMoney(analytics.max_base_salary, currencyCode)}
            />
          </section>
          <SalaryDistributionChart analytics={analytics} currencyCode={currencyCode} />
        </>
      ) : null}
    </>
  );
}

function SalaryDistributionChart({
  analytics,
  currencyCode,
}: {
  analytics: SalaryAnalyticsResponse;
  currencyCode: string | null;
}) {
  const minSalary = Number(analytics.min_base_salary ?? 0);
  const maxSalary = Number(analytics.max_base_salary ?? 0);
  const salaryBand = Math.max(maxSalary - minSalary, 0);
  const points = [
    { label: "Mean", value: analytics.mean_base_salary },
    { label: "Median", value: analytics.median_base_salary }
  ];

  return (
    <section className="panel chart-panel" aria-label="Salary distribution chart">
      <div className="chart-header">
        <div>
          <p className="metric-label">Salary distribution</p>
          <h3 className="chart-title">Mean and Median</h3>
        </div>
      </div>
      <div className="salary-band">
        <span>{formatMoney(analytics.min_base_salary, currencyCode)}</span>
        <span>{formatMoney(analytics.max_base_salary, currencyCode)}</span>
      </div>
      <div className="bar-chart">
        {points.map((point) => {
          const numericValue = Number(point.value ?? 0);
          const position =
            salaryBand > 0 ? Math.min(Math.max(((numericValue - minSalary) / salaryBand) * 100, 0), 100) : 50;

          return (
            <div className="bar-row" key={point.label}>
              <div className="bar-label">{point.label}</div>
              <div className="band-track">
                <div className="band-marker" style={{ left: `${position}%` }} />
              </div>
              <div className="bar-value">{formatMoney(point.value, currencyCode)}</div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function optionsFor(masterData: MasterData[], category: MasterData["category"]) {
  return masterData
    .filter((record) => record.category === category)
    .sort((left, right) => left.description.localeCompare(right.description));
}
