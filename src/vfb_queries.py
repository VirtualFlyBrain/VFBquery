import pysolr
from src.term_info_queries import deserialize_term_info
from vfb_connect.cross_server_tools import VfbConnect

vfb_solr = pysolr.Solr('http://solr.virtualflybrain.org/solr/vfb_json/', always_commit=False, timeout=990)
vc=VfbConnect()

def get_term_info(short_form: str):
    """
    Retrieves the term info for the given term short form.

    :param short_form: short form of the term
    :return: term info
    """
    termInfo = {}
    results = vfb_solr.search('id:' + short_form)
    print(results.raw_response)
    if results.hits > 0 and results.docs and len(results.docs) > 0:
        vfbTerm = deserialize_term_info(results.docs[0]['term_info'][0])
        queries = []
        meta = {
            "Name": "[%s](%s)"%(vfbTerm.term.core.label, vfbTerm.term.core.short_form),
            }
        meta["SuperTypes"] = vfbTerm.term.core.types
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
                images[image.channel_image.image.template_anatomy.short_form].append({"id":image.anatomy.short_form, "label": label, "thumbnail": image.channel_image.image.image_thumbnail.replace("http://","https://").replace("thumbnailT.png","thumbnail.png")})
                images[image.channel_image.image.template_anatomy.short_form].append({"id":image.anatomy.short_form, "label": label, "thumbnail_transparent": image.channel_image.image.image_thumbnail.replace("http://","https://").replace("thumbnail.png","thumbnailT.png")})
                for key in image.channel_image.image.keys():
                    if "images_" in key and not ("thumbnail" in key or "folder" in key):
                        images[image.channel_image.image.template_anatomy.short_form].append({"id":image.anatomy.short_form, "label": label, key.replace("image_",""): image.channel_image.image[key].replace("http://","https://")})
            termInfo["Examples"] = images
            queries.append({"query":"ListAllAvailableImages",label:"List all available images of %s"%(vfbTerm.term.core.label),"function":"get_instances","takes":[{"short_form":{"&&":["Class","Anatomy"]},"default":"%s"%(vfbTerm.term.core.short_form)}]})
        else:
            if vfbTerm.channel_image and len(vfbTerm.channel_image) > 0:
                images = {}
                for image in vfbTerm.channel_image:
                    label = vfbTerm.term.core.label
                    if vfbTerm.term.core.symbol != "" and len(vfbTerm.term.core.symbol) > 0:
                        label = vfbTerm.term.core.symbol
                    if not image.image.template_anatomy.short_form in images.keys():
                        images[image.image.template_anatomy.short_form]=[]
                    images[image.image.template_anatomy.short_form].append({"id":vfbTerm.term.core.short_form, "label": label, "thumbnail": image.image.image_thumbnail.replace("http://","https://").replace("thumbnailT.png","thumbnail.png")})
                    images[image.image.template_anatomy.short_form].append({"id":vfbTerm.term.core.short_form, "label": label, "thumbnail_transparent": image.image.image_thumbnail.replace("http://","https://").replace("thumbnail.png","thumbnailT.png")})
                    for key in image.image.keys():
                        if "images_" in key and not ("thumbnail" in key or "folder" in key):
                            images[image.image.template_anatomy.short_form].append({"id":vfbTerm.term.core.short_form, "label": label, key.replace("image_",""): image.image[key].replace("http://","https://")})
                termInfo["Thumbnails"] = images

        termInfo["Queries"] = queries
    else:
        print(f"No results found for ID '{short_form}'")
        print(results.raw_response)
    return termInfo

def get_instances(short_form: str):
    """
    Retrieves available instances for the given class short form.

    :param short_form: short form of the class
    :return: results rows
    """
    results = {"headers":{"label":{"title":"Name","type":"markdown","order":0,"sort":{0:"Asc"}},"parent":{"title":"Parent Type","type":"markdown","order":1},"template":{"title":"Template","type":"string","order":4},"tags":{"title":"Gross Types","type":"tags","order":3}},"rows":[]}
    rows = vc.get_instances(short_form, summary=True)

    for row in rows:
        label = row["symbol"]
        if label == "":
            label = row["label"]
        results["rows"].append({"label":"[%s](%s)"%(label,row["id"]),"parent":"[%s](%s)"%(row["parents_label"],row["parents_id"]),"template":row["templates"],"tags":row["tags"].split("|")})

    return results
