import { docs, meta } from '@/.source/server';
import { toFumadocsSource } from 'fumadocs-mdx/runtime/server';
import { loader } from 'fumadocs-core/source';

export const source = loader({
  baseUrl: '/',
  source: toFumadocsSource(docs, meta),
});
