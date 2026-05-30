import { PageHeader } from "@/components/PageHeader";
import { EmployeeDetailClient } from "./EmployeeDetailClient";

type EmployeeDetailPageProps = {
  searchParams: Promise<{ id?: string }>;
};

export default async function EmployeeDetailPage({ searchParams }: EmployeeDetailPageProps) {
  const { id } = await searchParams;

  return (
    <>
      <PageHeader eyebrow="Employee management" title="Manage employee" />
      {id ? (
        <EmployeeDetailClient employeeId={id} />
      ) : (
        <div className="status-message status-error">Employee id is required.</div>
      )}
    </>
  );
}
