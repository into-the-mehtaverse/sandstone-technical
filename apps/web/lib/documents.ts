/**
 * Minimal API client for documents: get and patch.
 * Backend returns snake_case (e.g. created_at, updated_at).
 */

const getBase = () =>
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ---- Response types (match backend) ----

export type DocumentSummary = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  version: number;
  party_id: string | null;
  party_name: string | null;
  doc_type: string | null;
};

export type Document = DocumentSummary & {
  content: string;
};

// ---- PATCH request (range-based replace) ----

export type ReplaceRange = {
  start: number;
  end: number;
};

export type DocumentChange = {
  operation: "replace";
  range: ReplaceRange;
  text: string;
};

// ---- API errors (shared error shape from backend) ----

export type ApiError = {
  error: string;
  code: number;
};

async function parseError(res: Response): Promise<ApiError> {
  let body: ApiError;
  try {
    body = await res.json();
  } catch {
    body = { error: res.statusText || "Request failed", code: res.status };
  }
  return body;
}

// ---- listDocuments ----

export type ListDocumentsFilters = {
  party_id?: string;
  party_name?: string;
  doc_type?: string;
};

/**
 * List document summaries (no content). Optional filters: party_id, party_name, doc_type.
 */
export async function listDocuments(
  filters: ListDocumentsFilters = {}
): Promise<DocumentSummary[]> {
  const params = new URLSearchParams();
  if (filters.party_id != null) params.set("party_id", filters.party_id);
  if (filters.party_name != null) params.set("party_name", filters.party_name);
  if (filters.doc_type != null) params.set("doc_type", filters.doc_type);
  const qs = params.toString();
  const url = `${getBase()}/documents${qs ? `?${qs}` : ""}`;
  const res = await fetch(url);
  if (!res.ok) {
    const err = await parseError(res);
    throw new Error(err.error || `HTTP ${err.code}`);
  }
  return res.json() as Promise<DocumentSummary[]>;
}

// ---- createFromTemplate ----

/**
 * Create a new document as a copy of a template. Returns the new document (use its id for editing).
 * Throws on 404 if template not found.
 */
export async function createFromTemplate(
  templateId: string,
  title?: string
): Promise<Document> {
  const url = `${getBase()}/documents/from-template`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ templateId, title }),
  });
  if (!res.ok) {
    const err = await parseError(res);
    throw new Error(err.error || `HTTP ${err.code}`);
  }
  return res.json() as Promise<Document>;
}

// ---- getDocument ----

/**
 * Fetch full document by id. Returns null if 304 (Not Modified).
 * Throws on 4xx/5xx with ApiError-shaped message.
 */
export async function getDocument(
  id: string,
  ifNoneMatchVersion?: number
): Promise<Document | null> {
  const url = `${getBase()}/documents/${encodeURIComponent(id)}`;
  const headers: HeadersInit = {};
  if (ifNoneMatchVersion != null) {
    headers["If-None-Match"] = String(ifNoneMatchVersion);
  }
  const res = await fetch(url, { headers });
  if (res.status === 304) return null;
  if (!res.ok) {
    const err = await parseError(res);
    throw new Error(err.error || `HTTP ${err.code}`);
  }
  return res.json() as Promise<Document>;
}

// ---- patchDocument ----

/**
 * Apply range-based changes to document. Sends If-Match: version.
 * Returns updated document. Throws on 404, 412 (version mismatch), 400 (e.g. out of range).
 */
export async function patchDocument(
  id: string,
  version: number,
  changes: DocumentChange[]
): Promise<Document> {
  const url = `${getBase()}/documents/${encodeURIComponent(id)}`;
  const res = await fetch(url, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      "If-Match": String(version),
    },
    body: JSON.stringify({ changes }),
  });
  if (!res.ok) {
    const err = await parseError(res);
    throw new Error(err.error || `HTTP ${err.code}`);
  }
  return res.json() as Promise<Document>;
}
