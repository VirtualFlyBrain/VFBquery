// Verbatim port of refineResults from
// openworm/geppetto-client@VFBv2.3.8.1 geppetto-ui/src/search/datasources/SOLRclient.tsx
// (TypeScript annotations stripped only).
function refineResults(docs, searchString) {
    var refinedResults = [];
    let seenRecords = new Set();
    const getRecordKey = (record) => {
        return Object.keys(record).sort().map(key => {
            let value = record[key];
            if (Array.isArray(value)) { value = [...value].sort().join("|"); }
            return key + ":" + value;
        }).join("||");
    };
    const pushUniqueRecord = (record) => {
        let recordKey = getRecordKey(record);
        if (!seenRecords.has(recordKey)) { seenRecords.add(recordKey); refinedResults.push(record); }
    };
    docs.map(item => {
        if (item.hasOwnProperty("synonym")) {
            item.synonym.map(innerItem => {
                let newRecord = {}
                if (innerItem !== item.label) {
                    Object.keys(item).map(key => {
                        switch(key) {
                            case "label": newRecord[key] = innerItem + " (" + item.label + ")"; break;
                            case "synonym": break;
                            default: newRecord[key] = item[key];
                        }
                    });
                    pushUniqueRecord(newRecord);
                }
            });
            let newRecord = {}
            Object.keys(item).map(key => {
                if (key !== "synonym") {
                    if (key === "label") { newRecord[key] = item[key] + " (" + item["short_form"] + ")"; }
                    else { newRecord[key] = item[key]; }
                }
            });
            pushUniqueRecord(newRecord);
        } else {
            let newRecord = {}
            Object.keys(item).map(key => {
                if (key === "label") { newRecord[key] = item[key] + " (" + item["short_form"] + ")"; }
                else { newRecord[key] = item[key]; }
            });
            pushUniqueRecord(newRecord);
        }
    });
    return refinedResults;
}
module.exports = { refineResults };
