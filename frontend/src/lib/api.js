// Single place that knows where the backend is and how to talk to it.
// Every call attaches the bearer token and funnels a 401 to the login page,
// which previously had to be repeated (and was sometimes forgotten) per component.

export const API_BASE =
    import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000';

export function getToken() {
    try {
        return localStorage.getItem('access_token');
    } catch {
        return null;
    }
}

export function clearToken() {
    try {
        localStorage.removeItem('access_token');
    } catch {
        /* private mode - nothing to clear */
    }
}

export class ApiError extends Error {
    constructor(message, status) {
        super(message);
        this.status = status;
    }
}

async function request(path, { method = 'GET', body, raw = false, auth = true } = {}) {
    const headers = {};
    if (body !== undefined) headers['Content-Type'] = 'application/json';

    if (auth) {
        const token = getToken();
        if (!token) throw new ApiError('Not signed in.', 401);
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${path}`, {
        method,
        headers,
        body: body === undefined ? undefined : JSON.stringify(body),
    });

    if (response.status === 401) {
        clearToken();
        throw new ApiError('Session expired. Please sign in again.', 401);
    }

    if (!response.ok) {
        let detail = `Request failed (${response.status})`;
        try {
            const data = await response.json();
            if (data?.detail) detail = typeof data.detail === 'string'
                ? data.detail : JSON.stringify(data.detail);
        } catch {
            /* non-JSON error body */
        }
        throw new ApiError(detail, response.status);
    }

    if (raw) return response;
    if (response.status === 204) return null;
    return response.json();
}

export const api = {
    get: (path, opts) => request(path, { ...opts, method: 'GET' }),
    post: (path, body, opts) => request(path, { ...opts, method: 'POST', body }),
    patch: (path, body, opts) => request(path, { ...opts, method: 'PATCH', body }),
    raw: (path, opts) => request(path, { ...opts, raw: true }),
};

// Turn an authenticated binary response into an object URL the browser can show.
// The artifact sandbox blocks <a download>, so callers open these in a new tab.
export async function fetchBlobUrl(path, { method = 'POST', body } = {}) {
    const response = await request(path, { method, body, raw: true });
    const blob = await response.blob();
    return URL.createObjectURL(blob);
}
