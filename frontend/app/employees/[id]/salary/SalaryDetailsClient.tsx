"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { getEmployee } from "@/lib/api";
import { formatMoney } from "@/lib/format";
import type { Employee } from "@/lib/types";

export function SalaryDetailsClient({ employeeId }: { employeeId: string }) {
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCurrent = true;

    async function loadEmployee() {
      setIsLoading(true);
      setError(null);
      try {
        const result = await getEmployee(employeeId);
        if (isCurrent) {
          setEmployee(result);
        }
      } catch (caught) {
        if (isCurrent) {
          setError(caught instanceof Error ? caught.message : "Unable to load salary details");
        }
      } finally {
        if (isCurrent) {
          setIsLoading(false);
        }
      }
    }

    loadEmployee();

    return () => {
      isCurrent = false;
    };
  }, [employeeId]);

  if (isLoading) {
    return <div className="status-message status-info">Loading salary history...</div>;
  }

  if (error) {
    return <div className="status-message status-error">{error}</div>;
  }

  if (!employee?.current_salary) {
    return <div className="status-message status-warning">No salary record is available.</div>;
  }

  const salary = employee.current_salary;

  return (
    <section className="panel">
      <div className="detail-grid salary-summary-grid">
        <DetailItem label="Employee" value={employee.full_name} />
        <DetailItem label="Employee ID" value={employee.employee_id} />
      </div>
      <div className="table-wrap section-gap">
        <table>
          <thead>
            <tr>
              <th>Effective from</th>
              <th>Effective to</th>
              <th>Currency</th>
              <th>Base salary</th>
              <th>Variable pay</th>
              <th>HRA allowance</th>
              <th>PF amount</th>
              <th>Gratuity</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{salary.effective_from}</td>
              <td>{salary.effective_to ?? "Current"}</td>
              <td>{salary.currency_code}</td>
              <td>{formatMoney(salary.base_amount, salary.currency_code)}</td>
              <td>{formatMoney(salary.variable_amount, salary.currency_code)}</td>
              <td>{formatMoney(salary.hra_allowance_amount, salary.currency_code)}</td>
              <td>{formatMoney(salary.pf_amount, salary.currency_code)}</td>
              <td>{formatMoney(salary.gratuity_amount, salary.currency_code)}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div className="actions">
        <Link className="button button-secondary" href={`/employees/${employee.id}`}>
          Back to employee
        </Link>
        <button className="button button-primary" disabled type="button">
          Revise
        </button>
      </div>
    </section>
  );
}

function DetailItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="detail-item">
      <p className="detail-label">{label}</p>
      <p className="detail-value">{value}</p>
    </div>
  );
}
