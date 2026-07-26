/*
 * Runs the REAL website sorter + refineResults under Node, so the Python port in
 * src/vfbquery/search_config.py can be diffed against it on identical Solr docs.
 *
 * Usage:  GEPPETTO_VFB=/path/to/geppetto-vfb node sort_under_node.js docs.json
 *
 * docs.json is {"query": "<raw search string>", "docs": [<solr docs>]}.
 * Prints {"refined_count": n, "rows": [[short_form, label], ...]} in sorted order.
 *
 * The sorter reads window.spotlightString, which SOLRclient.tsx sets to the
 * brace-escaped raw input — reproduced below.
 */
global.window = {};
const fs = require('fs');
const path = require('path');
const { refineResults } = require('./refine.js');

const gvfb = process.env.GEPPETTO_VFB || '/tmp/gvfb';
const configPath = path.join(gvfb, 'components/configuration/VFBMain/searchConfiguration.js');
const { searchConfiguration } = require(configPath);
const sorter = searchConfiguration.sorter;

const payload = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const searchString = payload.query.split('{').join('\\{').split('}').join('\\}');
window.spotlightString = searchString;

const refined = refineResults(payload.docs, searchString);
const sorted = refined.sort(sorter);
process.stdout.write(JSON.stringify({
  refined_count: refined.length,
  rows: sorted.map(r => [r.short_form, r.label]),
}));
