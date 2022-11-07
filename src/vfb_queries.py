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

    if vfbTerm.anatomy_channel_image and len(vfbTerm.anatomy_channel_image) > 0:
        images = {}
        for image in vfbTerm.anatomy_channel_image:
            label = image.anatomy.label
            if image.anatomy.symbol != "" and len(image.anatomy.symbol) > 0:
                label = image.anatomy.symbol
            if not image.channel_image.image.template_anatomy.short_form in images.keys():
                images[image.channel_image.image.template_anatomy.short_form]=[]
            images[image.channel_image.image.template_anatomy.short_form].append({"id":image.anatomy.short_form, "label": label, "thumbnail": image.channel_image.image.image_folder + "thumbnailT.png"})
        termInfo["Examples"] = images
    # TODO: Add Queries
    return termInfo

