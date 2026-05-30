import cors from "cors";
import express from "express";

const app = express();
const port = process.env.PORT || 10000;
const backendBaseUrl = process.env.BACKEND_BASE_URL;
const frontendOrigin = process.env.FRONTEND_ORIGIN || "*";

if (!backendBaseUrl) {
  throw new Error("BACKEND_BASE_URL is required");
}

app.use(cors({ origin: frontendOrigin }));
app.use(express.raw({ type: "*/*", limit: "10mb" }));

app.get("/", (_request, response) => {
  response.json({
    status: "ok",
    service: "salary-management-proxy",
    backend: backendBaseUrl,
  });
});

app.get("/health", async (_request, response, next) => {
  try {
    await proxyRequest({
      backendPath: "/health",
      request: _request,
      response,
    });
  } catch (error) {
    next(error);
  }
});

app.all("/api/:path(*)", async (request, response, next) => {
  try {
    await proxyRequest({
      backendPath: `/api/v1/${request.params.path}`,
      request,
      response,
    });
  } catch (error) {
    next(error);
  }
});

app.use((error, _request, response, _next) => {
  console.error(error);
  response.status(502).json({
    detail: "Unable to reach backend service.",
  });
});

app.listen(port, () => {
  console.log(`Salary Management proxy listening on ${port}`);
});

async function proxyRequest({ backendPath, request, response }) {
  const targetUrl = new URL(backendPath, backendBaseUrl);
  targetUrl.search = new URLSearchParams(request.query).toString();

  const headers = new Headers();
  for (const [key, value] of Object.entries(request.headers)) {
    if (typeof value !== "string") {
      continue;
    }
    if (["host", "content-length", "connection"].includes(key.toLowerCase())) {
      continue;
    }
    headers.set(key, value);
  }

  const backendResponse = await fetch(targetUrl, {
    method: request.method,
    headers,
    body: ["GET", "HEAD"].includes(request.method) ? undefined : request.body,
  });

  response.status(backendResponse.status);
  backendResponse.headers.forEach((value, key) => {
    if (!["content-encoding", "content-length", "transfer-encoding"].includes(key)) {
      response.setHeader(key, value);
    }
  });

  response.send(Buffer.from(await backendResponse.arrayBuffer()));
}
