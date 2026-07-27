/*
 * Runs the website's sorter + refineResults under Node, so the Python port in
 * src/vfbquery/search_config.py can be diffed against it on identical Solr docs.
 *
 * The two halves are not sourced the same way, and the difference matters when
 * reading a green result. The `sorter` is require()d live out of the
 * geppetto-vfb checkout at $GEPPETTO_VFB, so it is whatever that checkout holds
 * — update the checkout and the gate re-measures against the new comparator.
 * `refineResults` is not in the config file at all; it lives in SOLRclient.tsx
 * in the client package, so ./refine.js is a VERBATIM COPY pinned at
 * openworm/geppetto-client@VFBv2.3.8.1. That copy will not notice an upstream
 * change on its own: if refineResults moves, refresh refine.js by hand or this
 * harness will go on passing against a definition the website no longer uses.
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
