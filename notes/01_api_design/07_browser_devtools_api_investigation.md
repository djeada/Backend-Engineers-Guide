## Investigating Web APIs with Chrome DevTools: HackerTube Case Study

Chrome DevTools lets you study **the client-visible behavior** of a deployed website even when its backend source code is private. This is useful for learning API design, HTTP, browser storage, rendering, caching, and performance. It does **not** expose private server code or prove how the backend is implemented.

**Case study:** [HackerTube](https://hackertube.org/), a YouTube-style site built from videos recommended on Hacker News. Andrej Karpathy [describes](https://karpathy.bearblog.dev/hacker-tube/) its account-free recommendations, browser-side state, representative video-frame thumbnails, and downloadable dataset.

> **Evidence and scope (2026-11-02):** The endpoint names below are from [a third-party inspection of the website](https://trenchcoat.tools/b/Aq3O8h7v). The live site could not be fetched directly for independent verification while writing this note. Treat the table as a starting point for your own DevTools observations, not a complete or stable API contract. No Swagger/OpenAPI document has been confirmed.

### Prepare a clean investigation

1. Open [hackertube.org](https://hackertube.org/) in Chrome and press **F12**, or **Ctrl+Shift+I** (**Cmd+Option+I** on macOS).
2. Select **Network**, enable **Preserve log**, and choose **Fetch/XHR**. Reload the page.
3. Perform one action at a time: search, choose a topic, open a video, like it, and refresh. Note which requests appear after each action.
4. Select a request and inspect **Headers** (method, URL, status, headers, query parameters), **Payload**, **Preview/Response**, **Initiator**, and **Timing**.
5. Save evidence such as request method, route, parameter *names*, status, response shape, and timing. Do not paste private cookies, tokens, or browsing-history identifiers into public notes or videos.

### 1. Map the browser-visible API

A [third-party browser capture](https://trenchcoat.tools/b/Aq3O8h7v) reported these **GET requests observed on initial load**:

| Route | Reported role | Evidence |
| --- | --- | --- |
| `/api/browse` | Browse catalogue | Observed request |
| `/api/config` | Page configuration | Observed request |
| `/api/chips` | Topic/filter chips | Observed request |
| `/api/feed` | Recommendation feed | Observed request |

The same capture identified the following **strings in page HTML/source**. A reference is not evidence that the route currently works, what its HTTP method is, or which parameters it accepts:

| Candidate route | Feature to test | Evidence |
| --- | --- | --- |
| `/api/search` | Search | Referenced in frontend |
| `/api/video` | Video details | Referenced in frontend |
| `/api/related` | Related videos | Referenced in frontend |
| `/api/list` | Lists | Referenced in frontend |
| `/api/stats` | Statistics | Referenced in frontend |
| `/api/export` | Data export | Referenced in frontend |
| `/api/docs` | API documentation | Referenced in frontend |

An unofficial client has also been reported to use playlist-related routes (`/api/playlists` and `/api/playlist`); verify those yourself before treating them as part of the site API. Do not guess request bodies or attempt mutations on a third-party service.

**Experiment:** Compare the Network log before and after selecting a category or searching. Is the relevant filter in the query string, the request body, or computed entirely in the browser? Use **Initiator** to connect the request to the frontend code that triggered it.

### 2. Find documentation or Swagger/OpenAPI

An API base path such as `/api/` is **not** necessarily an API index. Likewise, a link to `/api/docs` does **not** establish that Swagger UI or a machine-readable OpenAPI schema exists.

In **Network**, click any documentation link the website actually exposes, and inspect its response and content type. Optionally check a small set of familiar **read-only** locations from the same-origin Console:

```javascript
const paths = [
  "/api/docs",
  "/openapi.json",
  "/api/openapi.json",
  "/swagger",
  "/swagger-ui"
];

const results = await Promise.all(paths.map(async (path) => {
  try {
    const response = await fetch(path, { method: "GET" });
    return {
      path,
      status: response.status,
      contentType: response.headers.get("content-type"),
      finalPath: new URL(response.url).pathname
    };
  } catch (error) {
    return { path, error: String(error) };
  }
}));
console.table(results);
```

**Interpretation:** `200` alone proves nothing; some SPAs return the homepage for unknown paths. Look for an OpenAPI document with an `openapi` version and `paths` object, or a UI explicitly rendering an API specification. A `404` only shows that *that particular URL* was not found. Avoid repeated guessing or scanning.

### 3. Inventory API requests from the Console

The Resource Timing API can quickly show same-origin resources with `/api/` in the path:

```javascript
console.table(
  performance.getEntriesByType("resource")
    .filter((entry) => {
      const url = new URL(entry.name);
      return url.origin === location.origin &&
             url.pathname.startsWith("/api/");
    })
    .map((entry) => {
      const url = new URL(entry.name);
      return {
        path: url.pathname,
        queryKeys: [...url.searchParams.keys()].join(", "),
        durationMs: Math.round(entry.duration)
      };
    })
);
```

Only parameter **names** are displayed to avoid accidentally exposing identifier or token values. Resource Timing is not a complete HTTP log: entries may be missing because of navigation, buffer limits, or timing rules. For method, status, request/response bodies, and headers, use **Network**.

### 4. Inspect large resources and caches

Use **Network → All**, sort by **Size** or **Time**, and look at waterfall, **Content-Encoding**, **Cache-Control**, `ETag`, transfer size, and the **Timing** breakdown. Compare a first load to a reload, with and without **Disable cache** checked (while DevTools is open).

This Console snippet surfaces the largest browser-recorded transfers:

```javascript
console.table(
  performance.getEntriesByType("resource")
    .map((entry) => ({
      path: new URL(entry.name).pathname,
      type: entry.initiatorType,
      transferKB: Math.round(entry.transferSize / 1024),
      durationMs: Math.round(entry.duration)
    }))
    .sort((a, b) => b.transferKB - a.transferKB)
    .slice(0, 20)
);
```

**Caveat:** `transferSize` may be zero for cached responses and for cross-origin resources without the appropriate timing-permission headers. Do not interpret zero as “no bandwidth was used.”

### 5. Test account-free personalization

Karpathy says HackerTube works without accounts and keeps user state locally. Use **Application → Local Storage**, **Session Storage**, **IndexedDB**, **Cookies**, and **Service Workers** to determine which mechanisms the current version actually uses.

1. Inspect the keys before interacting, without sharing their raw values.
2. Like or save a video, change a preference, and inspect which entries changed.
3. Reload, close/reopen the tab, and test a fresh incognito profile.
4. Watch **Network → Fetch/XHR** during these actions, especially requests involving the feed.
5. Determine whether state stays exclusively local or whether some state is transmitted to the server to compute recommendations.

**Important distinction:** “No account” does not imply “no requests or tracking.” An API can use locally stored preferences supplied with a request without maintaining registered users. Observing requests is not enough to infer internal ranking algorithms or data retention.

### 6. Investigate the thumbnail trick

HackerTube says it shows a **representative frame from the middle of the video** rather than the uploader's thumbnail.

1. Use **Network → Img** and reload.
2. If the site offers a thumbnail/frame toggle, switch it and compare URLs and request origins.
3. Open image **Preview**, inspect response headers and `Initiator`, and look for lazy loading or caching.
4. Verify whether the frame is generated by the app, obtained from another service, or retrieved as a stored image. The image URL alone may not tell the complete story.

### 7. Examine the shipped frontend, not the private server

Use **Sources** and **Network → JS** to identify bundles, source maps (if published), framework signatures, fetch calls, route strings, and event handlers. The **Pretty print** button (`{}`) can improve minified code readability; global search (**Ctrl+Shift+F**) helps find `fetch(`, `/api/`, `localStorage`, and request constructors.

Source maps might reveal readable client source, but **frontend JavaScript is not the server repository**. Do not infer the backend language or architecture merely from a filename or a request URL.

### 8. Measure page and interaction performance

- In **Performance**, record a fresh navigation, a search, and a video-open interaction; inspect main-thread work, network delays, layout shifts, and long tasks.
- In **Lighthouse**, run a reproducible mobile audit and record **LCP**, **CLS**, **INP** where available, accessibility, and performance findings. Lighthouse lab scores can vary between runs and don't by themselves measure real-user INP.
- In **Network**, compare cold load with warm cache, note connection/protocol information when available, and look for thumbnail downloads or large JavaScript bundles.
- In **Application**, check service worker and cache storage behavior before claiming assets are served offline.

### 9. Privacy and security checks (non-invasive)

In **Network**, inspect *which domains* receive requests and whether third-party video embeds are loaded before playback. In **Application**, view storage mechanisms; in **Security**, examine TLS details. For relevant responses, examine cookie attributes (`Secure`, `HttpOnly`, `SameSite`), CSP, CORS, and cache headers.

These observations reveal browser-facing behavior, **not** proof of full server security. Avoid attempting authentication bypasses, rate-limit testing, fuzzing, or submitting altered state to someone else's service.

### 10. Reproduce a single request safely

In **Network**, right-click a public **GET** request and choose **Copy → Copy as fetch** or **Copy as cURL**. Before using or publishing it, remove or redact `Cookie`, `Authorization`, tokens, personal IDs, sensitive query parameters, and unnecessary headers. Never distribute a live session's copied credentials. Don't automatically replay mutations or bulk-download data.

Record a small API inventory:

| Action | Method and route | Params/body (redacted) | Status | Response shape | Timing |
| --- | --- | --- | --- | --- | --- |
| Initial load | Fill from Network | — | — | — | — |
| Search | Fill from Network | — | — | — | — |
| Choose topic | Fill from Network | — | — | — | — |
| Open video | Fill from Network | — | — | — | — |
| Like/save video | Fill from Network (if any) | — | — | — | — |

### Demo outline for a technical video

1. **Hook:** Can we understand the client/backend boundary of a Claude-built site without the original source?
2. **Network:** Reload and enumerate initial requests; search and filter to discover more.
3. **API docs:** Test `/api/docs` and common OpenAPI locations, explaining the difference between a path reference and a real specification.
4. **Storage:** Like a video, inspect Local Storage, then retry in a clean session.
5. **Images:** Investigate the video-frame thumbnails.
6. **Sources:** Pretty-print frontend assets and locate request initiators.
7. **Performance/privacy:** Show a quick trace and third-party request inventory.
8. **Conclusion:** Separate **observed browser facts**, **plausible inferences**, and **unknown server behavior**.

### References

- [Andrej Karpathy — HackerTube (2026-10-31)](https://karpathy.bearblog.dev/hacker-tube/)
- [HackerTube website](https://hackertube.org/)
- [Third-party HackerTube network/source inspection](https://trenchcoat.tools/b/Aq3O8h7v) — external observation; verify against current behavior
- [Chrome DevTools: Network](https://developer.chrome.com/docs/devtools/network/)
- [Chrome DevTools: Storage](https://developer.chrome.com/docs/devtools/storage/)
- [MDN: PerformanceResourceTiming](https://developer.mozilla.org/en-US/docs/Web/API/PerformanceResourceTiming)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
