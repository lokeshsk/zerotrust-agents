// @ts-nocheck
import { default as __fd_glob_8 } from "../content/docs/meta.json?collection=meta"
import * as __fd_glob_7 from "../content/docs/quickstart.mdx?collection=docs"
import * as __fd_glob_6 from "../content/docs/proxies.mdx?collection=docs"
import * as __fd_glob_5 from "../content/docs/policy.mdx?collection=docs"
import * as __fd_glob_4 from "../content/docs/mcp.mdx?collection=docs"
import * as __fd_glob_3 from "../content/docs/index.mdx?collection=docs"
import * as __fd_glob_2 from "../content/docs/enterprise.mdx?collection=docs"
import * as __fd_glob_1 from "../content/docs/architecture.mdx?collection=docs"
import * as __fd_glob_0 from "../content/docs/api.mdx?collection=docs"
import { server } from 'fumadocs-mdx/runtime/server';
import type * as Config from '../source.config';

const create = server<typeof Config, import("fumadocs-mdx/runtime/types").InternalTypeConfig & {
  DocData: {
  }
}>({"doc":{"passthroughs":["extractedReferences"]}});

export const docs = await create.doc("docs", "content/docs", {"api.mdx": __fd_glob_0, "architecture.mdx": __fd_glob_1, "enterprise.mdx": __fd_glob_2, "index.mdx": __fd_glob_3, "mcp.mdx": __fd_glob_4, "policy.mdx": __fd_glob_5, "proxies.mdx": __fd_glob_6, "quickstart.mdx": __fd_glob_7, });

export const meta = await create.meta("meta", "content/docs", {"meta.json": __fd_glob_8, });