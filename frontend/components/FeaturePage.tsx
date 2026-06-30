import { ReactElement } from "react";

type FeaturePageProps = {
  title: string;
  description: string;
  children?: React.ReactNode;
};

export function FeaturePage({ title, description, children }: FeaturePageProps): ReactElement {
  return (
    <section className="space-y-4">
      <div className="card">
        <h2 className="text-2xl font-semibold">{title}</h2>
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-300">{description}</p>
      </div>
      {children}
    </section>
  );
}
