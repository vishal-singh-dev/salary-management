import { PageHeader } from "@/components/PageHeader";
import { EmployeeDetailClient } from "./EmployeeDetailClient";

type EmployeeDetailPageProps = {
  params: Promise<{ id: string }>;
};

export default async function EmployeeDetailPage({ params }: EmployeeDetailPageProps) {
  const { id } = await params;

  return (
    <>
      <PageHeader eyebrow="Employee management" title="Manage employee" />
      <EmployeeDetailClient employeeId={id} />
    </>
  );
}
