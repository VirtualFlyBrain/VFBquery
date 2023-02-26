import pysolr
from src.term_info_queries import deserialize_term_info
from vfb_connect.cross_server_tools import VfbConnect

# Connect to the VFB SOLR server
vfb_solr = pysolr.Solr('http://solr.virtualflybrain.org/solr/vfb_json/', always_commit=False, timeout=990)

# Create a VFB connection object for retrieving instances
vc = VfbConnect()

def get_term_info(short_form: str):
    """
    Retrieves the term info for the given term short form.

    :param short_form: short form of the term
    :return: term info
    """
    try:
        termInfo = {}
        # Search for the term in the SOLR server
        results = vfb_solr.search('id:' + short_form)
        # Check if any results were returned
        if results.hits > 0 and results.docs and len(results.docs) > 0:
            # Deserialize the term info from the first result
            vfbTerm = deserialize_term_info(results.docs[0]['term_info'][0])
            queries = []
            meta = {}
            meta["Name"] = "[%s](%s)"%(vfbTerm.term.core.label, vfbTerm.term.core.short_form)
            meta["SuperTypes"] = vfbTerm.term.core.types
            termInfo["meta"] = meta
            try:
                # Retrieve tags from the term's unique_facets attribute
                meta["Tags"] = vfbTerm.term.core.unique_facets
            except NameError:
                # If unique_facets attribute doesn't exist, use the term's types
                meta["Tags"] = vfbTerm.term.core.types
            try:
                # Retrieve description from the term's description attribute
                meta["Description"] = "%s"%("".join(vfbTerm.term.description))
            except NameError:
                pass
            try:
                # Retrieve comment from the term's comment attribute
                meta["Comment"] = "%s"%("".join(vfbTerm.term.comment))
            except NameError:
                pass
            except AttributeError:
                print(f"vfbTerm.term.comment: {vfbTerm.term}")
            termInfo["meta"] = meta
                
            # If the term has anatomy channel images, retrieve the images and associated information
            if vfbTerm.anatomy_channel_image and len(vfbTerm.anatomy_channel_image) > 0:
                images = {}
                for image in vfbTerm.anatomy_channel_image:
                    try:
                        record = {}
                        record["id"] = image.anatomy.short_form
                        label = image.anatomy.label
                        if image.anatomy.symbol != "" and len(image.anatomy.symbol) > 0:
                            label = image.anatomy.symbol
                        record["label"] = label
                        if not image.channel_image.image.template_anatomy.short_form in images.keys():
                            images[image.channel_image.image.template_anatomy.short_form]=[]
                        record["thumbnail"] = image.channel_image.image.image_thumbnail.replace("http://","https://").replace("thumbnailT.png","thumbnail.png")
                        record["thumbnail_transparent"] = image.channel_image.image.image_thumbnail.replace("http://","https://").replace("thumbnail.png","thumbnailT.png")
                        for key in vars(image.channel_image.image).keys():
                            if "image_" in key and not ("thumbnail" in key or "folder" in key):
                                record[key.replace("image_","")] = image.channel_image.image[key].replace("http://","https://")
                        images[image.channel_image.image.template_anatomy.short_form].append(record)
                    except AttributeError:
                        print (f"Error handling vfbTerm.anatomy_channel_image: {image}")   
                termInfo["Examples"] = images
                # add a query to `queries` list for listing all available images
                queries.append({"query":"ListAllAvailableImages",label:"List all available images of %s"%(vfbTerm.term.core.label),"function":"get_instances","takes":[{"short_form":{"&&":["Class","Anatomy"]},"default":"%s"%(vfbTerm.term.core.short_form)}]})
            else:
                # If the term has channel images but not anatomy channel images, create thumbnails from channel images.
                if vfbTerm.channel_image and len(vfbTerm.channel_image) > 0:
                    images = {}
                    for image in vfbTerm.channel_image:
                        record = {}
                        record["id"] = vfbTerm.term.core.short_form
                        label = vfbTerm.term.core.label
                        if vfbTerm.term.core.symbol != "" and len(vfbTerm.term.core.symbol) > 0:
                            label = vfbTerm.term.core.symbol
                        record["label"] = label
                        if not image.image.template_anatomy.short_form in images.keys():
                            images[image.image.template_anatomy.short_form]=[]
                        record["thumbnail"] = image.image.image_thumbnail.replace("http://","https://").replace("thumbnailT.png","thumbnail.png")
                        record["thumbnail_transparent"] = image.image.image_thumbnail.replace("http://","https://").replace("thumbnail.png","thumbnailT.png")
                        for key in vars(image.image).keys():
                            if "image_" in key and not ("thumbnail" in key or "folder" in key) and len(image.image[key]) > 1:
                                record[key.replace("image_","")] = image.image[key].replace("http://","https://")
                        images[image.image.template_anatomy.short_form].append(record)
                    # Add the thumbnails to the term info
                    termInfo["Thumbnails"] = images

            # Add the queries to the term info
            termInfo["Queries"] = queries
        else:
            print(f"No results found for ID '{short_form}'")
            print(results.raw_response)
    except IndexError:
            print(f"No results found for ID '{short_form}'")
            print("Error accessing SOLR server!")    
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
        # Create the label for the row using the symbol if available, otherwise the label
        label = row["symbol"]
        if label == "":
            label = row["label"]
        # Add the row to the results
        results["rows"].append({"label":"[%s](%s)"%(label,row["id"]),"parent":"[%s](%s)"%(row["parents_label"],row["parents_id"]),"template":row["templates"],"tags":row["tags"].split("|")})

    return results
