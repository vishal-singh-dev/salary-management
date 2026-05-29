"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { createEmployee, getNextEmployeeId } from "@/lib/api";
import type { EmployeeCreateInput } from "@/lib/types";

const initialForm: EmployeeCreateInput = {
  employee_id: "",
  full_name: "",
  title: "",
  department: "",
  country_code: "IN",
  from_date: "",
  initial_salary: {
    currency_code: "INR",
    base_amount: "",
    variable_amount: "0",
    hra_allowance_amount: "0",
    pf_amount: "0",
    gratuity_amount: "0",
    effective_from: "",
  },
};

export function EmployeeCreateForm() {
  const router = useRouter();
  const [form, setForm] = useState<EmployeeCreateInput>(initialForm);
  const [error, setError] = useState<string | null>(null);
  const [isLoadingEmployeeId, setIsLoadingEmployeeId] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    let isCurrent = true;
    const today = new Date().toISOString().slice(0, 10);
    setForm((current) => ({
      ...current,
      from_date: current.from_date || today,
      initial_salary: {
        ...current.initial_salary,
        effective_from: current.initial_salary.effective_from || today,
      },
    }));

    async function loadEmployeeId() {
      setIsLoadingEmployeeId(true);
      setError(null);
      try {
        const result = await getNextEmployeeId();
        if (isCurrent) {
          setForm((current) => ({ ...current, employee_id: result.employee_id }));
        }
      } catch (caught) {
        if (isCurrent) {
          setError(caught instanceof Error ? caught.message : "Unable to load next employee ID");
        }
      } finally {
        if (isCurrent) {
          setIsLoadingEmployeeId(false);
        }
      }
    }

    loadEmployeeId();

    return () => {
      isCurrent = false;
    };
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSaving(true);

    try {
      const employee = await createEmployee(form);
      router.push(`/employees/${employee.id}`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to create employee");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <form className="panel" onSubmit={handleSubmit}>
      <div className="form-grid">
        <TextField
          label="Employee ID"
          disabled
          onChange={() => undefined}
          required
          value={isLoadingEmployeeId ? "Loading..." : form.employee_id}
        />
        <TextField
          label="Full name"
          onChange={(value) => setForm((current) => ({ ...current, full_name: value }))}
          required
          value={form.full_name}
        />
        <TextField
          label="Job title"
          onChange={(value) => setForm((current) => ({ ...current, title: value }))}
          required
          value={form.title}
        />
        <TextField
          label="Department"
          onChange={(value) => setForm((current) => ({ ...current, department: value }))}
          required
          value={form.department}
        />
        <TextField
          label="Country code"
          maxLength={2}
          onChange={(value) =>
            setForm((current) => ({ ...current, country_code: value.toUpperCase() }))
          }
          required
          value={form.country_code}
        />
        <TextField
          label="Start date"
          onChange={(value) => setForm((current) => ({ ...current, from_date: value }))}
          required
          type="date"
          value={form.from_date}
        />
        <TextField
          label="Currency"
          maxLength={3}
          onChange={(value) =>
            setForm((current) => ({
              ...current,
              initial_salary: { ...current.initial_salary, currency_code: value.toUpperCase() },
            }))
          }
          required
          value={form.initial_salary.currency_code}
        />
        <TextField
          label="Base salary"
          onChange={(value) =>
            setForm((current) => ({
              ...current,
              initial_salary: { ...current.initial_salary, base_amount: value },
            }))
          }
          required
          type="number"
          value={form.initial_salary.base_amount}
        />
        <TextField
          label="Variable pay"
          onChange={(value) =>
            setForm((current) => ({
              ...current,
              initial_salary: { ...current.initial_salary, variable_amount: value },
            }))
          }
          type="number"
          value={form.initial_salary.variable_amount}
        />
        <TextField
          label="Salary effective from"
          onChange={(value) =>
            setForm((current) => ({
              ...current,
              initial_salary: { ...current.initial_salary, effective_from: value },
            }))
          }
          required
          type="date"
          value={form.initial_salary.effective_from}
        />
      </div>
      {error ? <div className="status-message status-error">{error}</div> : null}
      <div className="actions">
        <button
          className="button button-primary"
          disabled={isSaving || isLoadingEmployeeId || !form.employee_id}
          type="submit"
        >
          {isSaving ? "Creating..." : "Create employee"}
        </button>
      </div>
    </form>
  );
}

function TextField({
  label,
  value,
  onChange,
  type = "text",
  required = false,
  maxLength,
  disabled = false,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  required?: boolean;
  maxLength?: number;
  disabled?: boolean;
}) {
  const id = label.toLowerCase().replaceAll(" ", "-");
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        disabled={disabled}
        maxLength={maxLength}
        onChange={(event) => onChange(event.target.value)}
        required={required}
        type={type}
        value={value}
      />
    </div>
  );
}
