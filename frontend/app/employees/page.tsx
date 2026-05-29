import Link from "next/link";

import { PageHeader } from "@/components/PageHeader";
import { EmployeesClient } from "./EmployeesClient";

export default function EmployeesPage() {
  return (
    <>
      <PageHeader
        action={
          <Link className="button button-primary" href="/employees/new">
            Add employee
          </Link>
        }
        eyebrow="Employee management"
        title="Employees"
      />
      <EmployeesClient />
    </>
  );
}
