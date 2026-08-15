const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function analyzeEssay(essay) {
  let response;
  try {
    response = await fetch(`${API_URL}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ essay }),
    });
  } catch {
    throw new Error(
      `Could not reach the analysis API at ${API_URL}. Is the backend running?`
    );
  }

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}.`;
    try {
      const data = await response.json();
      if (data && data.detail) {
        detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
      }
    } catch {
      // response body wasn't JSON; keep the generic message
    }
    throw new Error(detail);
  }

  return response.json();
}
