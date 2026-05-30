"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { deleteEmployee, getEmployee, listMasterData, updateEmployee } from "@/lib/api";
import { formatMoney } from "@/lib/format";
import { fallbackMasterData, labelFor, optionsFor } from "@/lib/masterData";
import type { Employee, EmployeeUpdateInput, MasterData } from "@/lib/types";

export function EmployeeDetailClient({ employeeId }: { employeeId: string }) {
  const router = useRouter();
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [form, setForm] = useState<EmployeeUpdateInput>({});
  const [masterData, setMasterData] = useState<MasterData[]>(fallbackMasterData);
  const [isEditing, setIsEditing] = useState(false);
  const [isSalaryModalOpen, setIsSalaryModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
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
          setForm(formFromEmployee(result));
        }
      } catch (caught) {
        if (isCurrent) {
          setError(caught instanceof Error ? caught.message : "Unable to load employee");
        }
      } finally {
        if (isCurrent) {
          setIsLoading(false);
        }
      }
    }

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

    loadEmployee();
    loadMasterData();

    return () => {
      isCurrent = false;
    };
  }, [employeeId]);

  async function handleDelete() {
    const shouldDelete = window.confirm(
      "Delete this employee from active records? The profile remains available for audit history.",
    );
    if (!shouldDelete) {
      return;
    }

    setError(null);
    try {
      await deleteEmployee(employeeId);
      router.push("/employees");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to delete employee");
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (!hasValidEmploymentDates(form)) {
      setError("Employment end date must be later than employment start date.");
      return;
    }

    setIsSaving(true);

    try {
      const updatedEmployee = await updateEmployee(employeeId, form);
      setEmployee(updatedEmployee);
      setForm(formFromEmployee(updatedEmployee));
      setIsEditing(false);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to update employee");
    } finally {
      setIsSaving(false);
    }
  }

  if (isLoading) {
    return <div className="status-message status-info">Loading employee...</div>;
  }

  if (error && !employee) {
    return <div className="status-message status-error">{error}</div>;
  }

  if (!employee) {
    return <div className="status-message status-warning">Employee not found.</div>;
  }

  const isInactive = employee.to_date !== null;
  const countryOptions = optionsFor(masterData, "country");
  const departmentOptions = optionsFor(masterData, "department");
  const titleOptions = optionsFor(masterData, "job_title");

  return (
    <form className="panel" onSubmit={handleSubmit}>
      <div className="detail-grid">
        <DetailItem label="Employee ID" value={employee.employee_id} />
        <EditableField
          disabled={!isEditing}
          label="Full name"
          onChange={(value) => setForm((current) => ({ ...current, full_name: value }))}
          value={form.full_name ?? ""}
        />
        <EditableSelectField
          disabled={!isEditing}
          label="Job title"
          onChange={(value) => setForm((current) => ({ ...current, title: value }))}
          options={titleOptions}
          readValue={labelFor(masterData, "job_title", form.title ?? "")}
          value={form.title ?? ""}
        />
        <EditableSelectField
          disabled={!isEditing}
          label="Department"
          onChange={(value) => setForm((current) => ({ ...current, department: value }))}
          options={departmentOptions}
          readValue={labelFor(masterData, "department", form.department ?? "")}
          value={form.department ?? ""}
        />
        <EditableSelectField
          disabled={!isEditing}
          label="Country"
          onChange={(value) => setForm((current) => ({ ...current, country_code: value }))}
          options={countryOptions}
          readValue={labelFor(masterData, "country", form.country_code ?? "")}
          value={form.country_code ?? ""}
        />
        <EditableField
          disabled={!isEditing}
          label="Employment start"
          onChange={(value) => setForm((current) => ({ ...current, from_date: value }))}
          type="date"
          value={form.from_date ?? ""}
        />
        <EditableField
          disabled={!isEditing}
          label="Employment end"
          onChange={(value) =>
            setForm((current) => ({ ...current, to_date: value === "" ? null : value }))
          }
          type="date"
          value={form.to_date ?? ""}
        />
        <DetailItem
          label="Status"
          value={employee.to_date ? `Inactive since ${employee.to_date}` : "Active"}
        />
      </div>
      {error ? <div className="status-message status-error">{error}</div> : null}
      <div className="actions">
        <button
          className="button button-secondary"
          onClick={() => setIsSalaryModalOpen(true)}
          type="button"
        >
          Salary details
        </button>
        {isEditing ? (
          <>
            <button
              className="button button-secondary"
              onClick={() => {
                setForm(formFromEmployee(employee));
                setIsEditing(false);
              }}
              type="button"
            >
              Cancel
            </button>
            <button className="button button-primary" disabled={isSaving} type="submit">
              {isSaving ? "Saving..." : "Save changes"}
            </button>
          </>
        ) : (
          <button
            className="button button-primary"
            disabled={isInactive}
            onClick={() => setIsEditing(true)}
            type="button"
          >
            Update
          </button>
        )}
        <button
          className="button button-danger"
          disabled={isInactive}
          onClick={handleDelete}
          type="button"
        >
          Delete
        </button>
      </div>
      {isInactive ? (
        <div className="status-message status-info">
          This employee is inactive, so profile changes are locked.
        </div>
      ) : null}
      {isSalaryModalOpen ? (
        <SalaryStructureModal employee={employee} onClose={() => setIsSalaryModalOpen(false)} />
      ) : null}
    </form>
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

function EditableField({
  label,
  value,
  onChange,
  disabled,
  type = "text",
  maxLength,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  disabled: boolean;
  type?: string;
  maxLength?: number;
}) {
  const id = label.toLowerCase().replaceAll(" ", "-");
  return (
    <div className="detail-item editable-detail">
      <label className="detail-label" htmlFor={id}>
        {label}
      </label>
      <input
        disabled={disabled}
        id={id}
        maxLength={maxLength}
        onChange={(event) => onChange(event.target.value)}
        type={type}
        value={value}
      />
    </div>
  );
}

function EditableSelectField({
  label,
  value,
  readValue,
  onChange,
  options,
  disabled,
}: {
  label: string;
  value: string;
  readValue: string;
  onChange: (value: string) => void;
  options: MasterData[];
  disabled: boolean;
}) {
  const id = label.toLowerCase().replaceAll(" ", "-");
  return (
    <div className="detail-item editable-detail">
      <label className="detail-label" htmlFor={id}>
        {label}
      </label>
      {disabled ? (
        <input disabled id={id} value={readValue} />
      ) : (
        <select id={id} onChange={(event) => onChange(event.target.value)} value={value}>
          <option value="">Select {label.toLowerCase()}</option>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.description}
            </option>
          ))}
        </select>
      )}
    </div>
  );
}

function SalaryStructureModal({
  employee,
  onClose,
}: {
  employee: Employee;
  onClose: () => void;
}) {
  const salary = employee.current_salary;

  return (
    <div className="modal-backdrop" role="presentation">
      <section
        aria-labelledby="salary-structure-title"
        aria-modal="true"
        className="modal-panel"
        role="dialog"
      >
        <div className="modal-header">
          <div>
            <p className="eyebrow">Current salary</p>
            <h3 className="modal-title" id="salary-structure-title">
              {employee.full_name}
            </h3>
          </div>
          <button
            aria-label="Close salary details"
            className="icon-button"
            onClick={onClose}
            type="button"
          >
            X
          </button>
        </div>
        {salary ? (
          <div className="detail-grid">
            <DetailItem
              label="Base salary"
              value={formatMoney(salary.base_amount, salary.currency_code)}
            />
            <DetailItem
              label="Variable pay"
              value={formatMoney(salary.variable_amount, salary.currency_code)}
            />
            <DetailItem
              label="HRA allowance"
              value={formatMoney(salary.hra_allowance_amount, salary.currency_code)}
            />
            <DetailItem label="PF amount" value={formatMoney(salary.pf_amount, salary.currency_code)} />
            <DetailItem label="Gratuity" value={formatMoney(salary.gratuity_amount, salary.currency_code)} />
            <DetailItem label="Currency" value={salary.currency_code} />
            <DetailItem label="Effective from" value={salary.effective_from} />
            <DetailItem label="Effective to" value={salary.effective_to ?? "Current"} />
          </div>
        ) : (
          <div className="status-message status-warning">No salary record is available.</div>
        )}
        <div className="modal-actions">
          <Link className="button button-primary" href={`/employees/${employee.id}/salary`}>
            Manage
          </Link>
        </div>
      </section>
    </div>
  );
}

function hasValidEmploymentDates(form: EmployeeUpdateInput): boolean {
  if (!form.from_date || !form.to_date) {
    return true;
  }

  return form.from_date < form.to_date;
}

function formFromEmployee(employee: Employee): EmployeeUpdateInput {
  return {
    full_name: employee.full_name,
    title: employee.title,
    department: employee.department,
    country_code: employee.country_code,
    from_date: employee.from_date,
    to_date: employee.to_date,
  };
}
