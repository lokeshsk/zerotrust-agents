// @ts-nocheck
import { browser } from 'fumadocs-mdx/runtime/browser';
import type * as Config from '../source.config';

const create = browser<typeof Config, import("fumadocs-mdx/runtime/types").InternalTypeConfig & {
  DocData: {
  }
}>();
const browserCollections = {
  docs: create.doc("docs", {"api.mdx": () => import("../content/docs/api.mdx?collection=docs"), "architecture.mdx": () => import("../content/docs/architecture.mdx?collection=docs"), "cli.mdx": () => import("../content/docs/cli.mdx?collection=docs"), "enterprise.mdx": () => import("../content/docs/enterprise.mdx?collection=docs"), "index.mdx": () => import("../content/docs/index.mdx?collection=docs"), "mcp.mdx": () => import("../content/docs/mcp.mdx?collection=docs"), "policy.mdx": () => import("../content/docs/policy.mdx?collection=docs"), "proxies.mdx": () => import("../content/docs/proxies.mdx?collection=docs"), "quickstart.mdx": () => import("../content/docs/quickstart.mdx?collection=docs"), "security-labs.mdx": () => import("../content/docs/security-labs.mdx?collection=docs"), "templates.mdx": () => import("../content/docs/templates.mdx?collection=docs"), }),
};
export default browserCollections;