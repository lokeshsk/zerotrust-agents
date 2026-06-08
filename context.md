# ZeroTrust Agents Context & Handoff

This document provides exact technical context for future AI assistants or developers resuming work on the ZeroTrust Agents project. It explains where we are, what we are building, and what needs to happen next.

## 1. What Are We Building?
We are building an Enterprise Security Gateway for AI Agents. It intercepts LLM API traffic, evaluates tool/function calls against a Policy Engine, and blocks unauthorized or malicious requests. We are explicitly building this to be a multi-tenant B2B SaaS product capable of charging enterprise organizations based on traffic volume.

## 2. Where Are We Right Now?
**Status: The Multi-Tenant Schema and UI scaffolding are complete, but Auth0 integration is pending.**

What is completely finished:
*   **The Database Schema**: `apps/api/models.py` has been rewritten. We introduced a `TenantDB` model. All core tables (`PolicyDB`, `AuditLogDB`, `PendingApprovalDB`) now belong to a `tenant_id`.
*   **The Proxy Logic**: `apps/gateway/routers/openai_proxy.py` intercepts `x-tenant-id` from HTTP headers and passes it down to the Policy Engine.
*   **The Billing Engine**: `apps/api/routers/logs.py` increments `events_this_month` for a tenant every time an audit log is created.
*   **The Dashboard UI**: We have built an Enterprise Pricing landing page, the Auto-Discovery Graph (using `react-flow`), and added "Enterprise SSO" buttons to the UI.

**The Current Mock State**: 
Because we haven't fully integrated Auth0 yet, the Next.js UI does NOT send a `tenant_id` header in its API requests. To prevent the app from crashing, `apps/api/main.py` automatically seeds a `"default"` tenant into the database, and the Python APIs fallback to `"default"` if no tenant is provided.

## 3. What Are The Exact Next Steps?

To turn this into a fully functioning SaaS product, the following steps must be executed in order:

### Phase 1: Auth0 JWT Backend Validation
We have the SSO button on the frontend, but the backend doesn't know how to secure routes.
*   **Action**: Update `apps/api/routers/auth.py` to include a FastAPI dependency (`Depends(verify_jwt)`).
*   **Details**: This dependency must intercept the `Authorization: Bearer <token>` header, validate the JWT against the Auth0 JWKS endpoint, and extract the `tenant_id` and `user_id` from the payload.
*   **Goal**: Replace the insecure `"default"` fallback with real cryptographic validation.

### Phase 2: Frontend Tenant Switcher
*   **Action**: Update the Next.js Dashboard (`apps/web/src/app/page.tsx`).
*   **Details**: When a user logs in via Auth0, they may belong to multiple Enterprise Workspaces. Build a dropdown component in the sidebar to let them switch active tenants.
*   **Goal**: Ensure all `fetch()` calls in the frontend attach `x-tenant-id: <selected_tenant>` to the headers.

### Phase 3: Alembic Database Migrations
*   **Action**: Initialize Alembic for the `apps/api` directory.
*   **Details**: Currently, `main.py` runs `Base.metadata.create_all()`. This is fine for prototyping but terrible for production because it cannot alter existing tables if the schema changes.
*   **Goal**: Generate the first `alembic revision --autogenerate` so we can safely update the database schema in the future.

### Phase 4: Advanced Semantic DLP (Future)
*   **Action**: Replace the Regex-based DLP in `openai_proxy.py`.
*   **Details**: Currently, the gateway blocks things like `DROP TABLE` using Regex. This is easily bypassed by LLMs.
*   **Goal**: Implement an ultra-fast secondary, smaller LLM (e.g., Llama-3-8B locally or Claude Haiku) inside the Proxy to semantically classify if a payload is malicious before forwarding it to the main Agent LLM.
