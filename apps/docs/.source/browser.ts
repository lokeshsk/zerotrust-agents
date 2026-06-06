// @ts-nocheck
import { browser } from 'fumadocs-mdx/runtime/browser';
import type * as Config from '../source.config';

const create = browser<typeof Config, import("fumadocs-mdx/runtime/types").InternalTypeConfig & {
  DocData: {
  }
}>();
const browserCollections = {
  docs: create.doc("docs", {"architecture.mdx": () => import("../content/docs/architecture.mdx?collection=docs"), "enterprise.mdx": () => import("../content/docs/enterprise.mdx?collection=docs"), "index.mdx": () => import("../content/docs/index.mdx?collection=docs"), "mcp.mdx": () => import("../content/docs/mcp.mdx?collection=docs"), "proxies.mdx": () => import("../content/docs/proxies.mdx?collection=docs"), "quickstart.mdx": () => import("../content/docs/quickstart.mdx?collection=docs"), }),
};
export default browserCollections;