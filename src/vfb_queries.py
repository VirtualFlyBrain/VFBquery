import pysolr
from src.term_info_queries import deserialize_term_info

def get_term_info(short_form: str):
    """
    Retrieves the term info for the given term short form.

    :param short_form: short form of the term
    :return: term info
    """
    termInfo = {}
    vfb_solr = pysolr.Solr('http://query.virtualflybrain.org:8983/solr/vfb_json/', always_commit=True, timeout=990)
    results = vfb_solr.search('id:' + short_form)
    vfbTerm = deserialize_term_info(results.docs[0]['term_info'][0])
    meta = {
        "Name": "[%s](%s)"%(vfbTerm.term.core.label, vfbTerm.term.core.short_form),
        }
    try:
        meta["Tags"] = vfbTerm.term.core.unique_facets
    except NameError:
        meta["Tags"] = vfbTerm.term.core.types
    try:
        meta["Description"] = "%s"%("".join(vfbTerm.term.description))
    except NameError:
        pass
    try:
        meta["Comment"] = "%s"%("".join(vfbTerm.term.comment))
    except NameError:
        pass
    termInfo["meta"] = meta
    
    # TODO: Add Queries
    return termInfo

