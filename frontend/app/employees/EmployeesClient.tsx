"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { listEmployees, listMasterData } from "@/lib/api";
import { formatMoney } from "@/lib/format";
import { fallbackMasterData, labelFor } from "@/lib/masterData";
import type { EmployeeListResponse, MasterData } from "@/lib/types";

const pageSize = 25;

export function EmployeesClient() {
  const [offset, setOffset] = useState(0);
  const [includeInactive, setIncludeInactive] = useState(false);
  const [employees, setEmployees] = useState<EmployeeListResponse | null>(null);
  const [masterData, setMasterData] = useState<MasterData[]>(fallbackMasterData);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCurrent = true;

    async function loadEmployees() {
      setIsLoading(true);
      setError(null);
      try {
        const result = await listEmployees({ limit: pageSize, offset, includeInactive });
        if (isCurrent) {
          setEmployees(result);
        }
      } catch (caught) {
        if (isCurrent) {
          setError(caught instanceof Error ? caught.message : "Unable to load employees");
        }
      } finally {
        if (isCurrent) {
          setIsLoading(false);
        }
      }
    }

    loadEmployees();

    return () => {
      isCurrent = false;
    };
  }, [offset, includeInactive]);

  useEffect(() => {
    let isCurrent = true;

    async function loadMasterData() {
      try {
        const result = await listMasterData();
        if (isCurrent) {
          setMasterData(result);
        }
      } catch {
        if (isCurrent) {
          setMasterData(fallbackMasterData);
        }
      }
    }

    loadMasterData();

    return () => {
      isCurrent = false;
    };
  }, []);

  const canMoveBack = offset > 0;
  const canMoveForward = employees ? offset + employees.limit < employees.total : false;

  return (
    <section className="panel">
      <div className="actions" style={{ justifyContent: "space-between", marginTop: 0 }}>
        <label className="checkbox-row" style={{ paddingTop: 0 }}>
          <input
            checked={includeInactive}
            onChange={(event) => {
              setOffset(0);
              setIncludeInactive(event.target.checked);
            }}
            type="checkbox"
          />
          Include inactive employees
        </label>
        <div>
          <button
            className="button button-secondary"
            disabled={!canMoveBack}
            onClick={() => setOffset((current) => Math.max(0, current - pageSize))}
            type="button"
          >
            Previous
          </button>{" "}
          <button
            className="button button-secondary"
            disabled={!canMoveForward}
            onClick={() => setOffset((current) => current + pageSize)}
            type="button"
          >
            Next
          </button>
        </div>
      </div>

      {isLoading ? <div className="status-message status-info">Loading employees...</div> : null}
      {error ? <div className="status-message status-error">{error}</div> : null}

      {!isLoading && !error && employees?.items.length === 0 ? (
        <div className="status-message status-warning">No employees found.</div>
      ) : null}

      {!isLoading && !error && employees?.items.length ? (
        <>
          <div className="table-wrap section-gap">
            <table>
              <thead>
                <tr>
                  <th>Employee ID</th>
                  <th>Name</th>
                  <th>Title</th>
                  <th>Department</th>
                  <th>Country</th>
                  <th>Current salary</th>
                </tr>
              </thead>
              <tbody>
                {employees.items.map((employee) => (
                  <tr key={employee.id}>
                    <td>
                      <Link href={`/employees/${employee.id}`}>{employee.employee_id}</Link>
                    </td>
                    <td>{employee.full_name}</td>
                    <td>{labelFor(masterData, "job_title", employee.title)}</td>
                    <td>{labelFor(masterData, "department", employee.department)}</td>
                    <td>{labelFor(masterData, "country", employee.country_code)}</td>
                    <td>
                      {formatMoney(
                        employee.current_salary?.base_amount ?? null,
                        employee.current_salary?.currency_code,
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="page-description">
            Showing {offset + 1} to {Math.min(offset + employees.limit, employees.total)} of{" "}
            {employees.total} employees.
          </p>
        </>
      ) : null}
    </section>
  );
}
