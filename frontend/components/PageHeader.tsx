type PageHeaderProps = {
  eyebrow: string;
  title: string;
  action?: React.ReactNode;
};

export function PageHeader({ eyebrow, title, action }: PageHeaderProps) {
  return (
    <header className="page-header">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h2 className="page-title">{title}</h2>
      </div>
      {action}
    </header>
  );
}
