import { PageHeader } from "@/components/PageHeader";
import { EmployeeCreateForm } from "./EmployeeCreateForm";

export default function NewEmployeePage() {
  return (
    <>
      <PageHeader
        eyebrow="Employee management"
        title="Add employee"
      />
      <EmployeeCreateForm />
    </>
  );
}
