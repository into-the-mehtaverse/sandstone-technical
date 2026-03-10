"use client";

import { cn } from "@/lib/utils";
import type { DocumentSummary } from "@/lib/documents";

/** Single template card: blue background, white “page” with horizontal lines. */
function TemplateCard({
  template,
  onClick,
  disabled,
  className,
}: {
  template: DocumentSummary;
  onClick: () => void;
  disabled?: boolean;
  className?: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "group flex flex-col items-center gap-2 rounded-lg p-4 text-left transition hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        "bg-blue-600",
        disabled && "cursor-not-allowed opacity-70",
        className
      )}
      aria-label={`Use template: ${template.title}`}
    >
      {/* White rectangle (top half of page) with lines */}
      <div className="w-full max-w-[140px] flex-shrink-0 overflow-hidden rounded-sm bg-white shadow-md">
        <div className="aspect-[3/4] flex flex-col justify-start pt-2 px-3 pb-1">
          {[0, 1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="h-2 w-full rounded-full bg-gray-200 mt-1 first:mt-0"
              aria-hidden
            />
          ))}
        </div>
      </div>
      <span className="text-sm font-medium text-white line-clamp-2">
        {template.title}
      </span>
    </button>
  )
}

export type TemplateListProps = {
  templates: DocumentSummary[];
  onSelectTemplate: (templateId: string) => void;
  /** When set, the list is disabled (e.g. creating an instance). */
  disabled?: boolean;
  className?: string;
};

export function TemplateList({
  templates,
  onSelectTemplate,
  disabled = false,
  className,
}: TemplateListProps) {
  if (templates.length === 0) {
    return (
      <p className="text-muted-foreground text-sm">No templates found.</p>
    );
  }

  return (
    <ul
      className={cn("grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4", className)}
      role="list"
    >
      {templates.map((template) => (
        <li key={template.id}>
          <TemplateCard
            template={template}
            onClick={() => onSelectTemplate(template.id)}
            disabled={disabled}
          />
        </li>
      ))}
    </ul>
  );
}
