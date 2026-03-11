"use client";

import { BugIcon } from "@phosphor-icons/react";
import { useState } from "react";

type Kind = "bug_report" | "feature_request";

export function BugReportFab() {
  const [open, setOpen] = useState(false);
  const [kind, setKind] = useState<Kind>("bug_report");
  const [message, setMessage] = useState("");

  return (
    <div className="fixed left-6 top-[5.5rem] z-20 flex flex-col gap-3">
      {open ? (
        <div className="flex flex-col gap-2 w-72 rounded-xl border border-border bg-background p-3 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-foreground">Feedback</span>
            <button
              type="button"
              onClick={() => setOpen(false)}
              className="text-muted-foreground hover:text-foreground text-sm"
              aria-label="Close"
            >
              ×
            </button>
          </div>
          <select
            value={kind}
            onChange={(e) => setKind(e.target.value as Kind)}
            className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="bug_report">Bug report</option>
            <option value="feature_request">Feature request</option>
          </select>
          <textarea
            placeholder="Describe the issue or idea..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={3}
            className="w-full resize-none rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
          <button
            type="button"
            onClick={() => {
              setMessage("");
              setOpen(false);
            }}
            className="rounded-lg bg-primary px-3 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
          >
            Send
          </button>
        </div>
      ) : null}
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-border bg-background text-foreground shadow hover:bg-muted focus:outline-none focus:ring-2 focus:ring-ring"
        aria-label="Report a bug or request a feature"
      >
        <BugIcon className="size-5" weight="regular" />
      </button>
    </div>
  );
}
