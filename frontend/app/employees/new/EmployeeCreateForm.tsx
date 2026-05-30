"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { createEmployee, getNextEmployeeId, listMasterData } from "@/lib/api";
import { fallbackMasterData, optionsFor } from "@/lib/masterData";
import type { EmployeeCreateInput, MasterData } from "@/lib/types";

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
  const [masterData, setMasterData] = useState<MasterData[]>(fallbackMasterData);
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

    loadEmployeeId();
    loadMasterData();

    return () => {
      isCurrent = false;
    };
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    const salaryValidationError = validateSalaryAmounts(form.initial_salary);
    if (salaryValidationError) {
      setError(salaryValidationError);
      return;
    }

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

  const countryOptions = optionsFor(masterData, "country");
  const departmentOptions = optionsFor(masterData, "department");
  const titleOptions = optionsFor(masterData, "job_title");

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
        <SelectField
          label="Job title"
          onChange={(value) => setForm((current) => ({ ...current, title: value }))}
          options={titleOptions}
          required
          value={form.title}
        />
        <SelectField
          label="Department"
          onChange={(value) => setForm((current) => ({ ...current, department: value }))}
          options={departmentOptions}
          required
          value={form.department}
        />
        <SelectField
          label="Country"
          onChange={(value) => setForm((current) => ({ ...current, country_code: value }))}
          options={countryOptions}
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
          min="0.01"
          step="0.01"
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
          min="0"
          step="0.01"
          value={form.initial_salary.variable_amount}
        />
        <TextField
          label="HRA allowance"
          onChange={(value) =>
            setForm((current) => ({
              ...current,
              initial_salary: { ...current.initial_salary, hra_allowance_amount: value },
            }))
          }
          min="0"
          step="0.01"
          type="number"
          value={form.initial_salary.hra_allowance_amount}
        />
        <TextField
          label="PF amount"
          onChange={(value) =>
            setForm((current) => ({
              ...current,
              initial_salary: { ...current.initial_salary, pf_amount: value },
            }))
          }
          min="0"
          step="0.01"
          type="number"
          value={form.initial_salary.pf_amount}
        />
        <TextField
          label="Gratuity amount"
          onChange={(value) =>
            setForm((current) => ({
              ...current,
              initial_salary: { ...current.initial_salary, gratuity_amount: value },
            }))
          }
          min="0"
          step="0.01"
          type="number"
          value={form.initial_salary.gratuity_amount}
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
  min,
  step,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  required?: boolean;
  maxLength?: number;
  disabled?: boolean;
  min?: string;
  step?: string;
}) {
  const id = label.toLowerCase().replaceAll(" ", "-");
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        disabled={disabled}
        min={min}
        maxLength={maxLength}
        onChange={(event) => onChange(event.target.value)}
        required={required}
        step={step}
        type={type}
        value={value}
      />
    </div>
  );
}

function validateSalaryAmounts(salary: EmployeeCreateInput["initial_salary"]): string | null {
  const baseAmount = Number(salary.base_amount);
  if (!Number.isFinite(baseAmount) || baseAmount <= 0) {
    return "Base salary must be greater than 0.";
  }

  const salaryFields = [
    ["Variable pay", salary.variable_amount],
    ["HRA allowance", salary.hra_allowance_amount],
    ["PF amount", salary.pf_amount],
    ["Gratuity amount", salary.gratuity_amount],
  ] as const;

  for (const [label, value] of salaryFields) {
    const amount = Number(value);
    if (!Number.isFinite(amount) || amount < 0) {
      return `${label} must be 0 or greater.`;
    }
  }

  return null;
}

function SelectField({
  label,
  value,
  onChange,
  options,
  required = false,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: MasterData[];
  required?: boolean;
}) {
  const id = label.toLowerCase().replaceAll(" ", "-");
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <select
        id={id}
        onChange={(event) => onChange(event.target.value)}
        required={required}
        value={value}
      >
        <option value="">Select {label.toLowerCase()}</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.description}
          </option>
        ))}
      </select>
    </div>
  );
}
