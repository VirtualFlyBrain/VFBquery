import pysolr
from term_info_queries import deserialize_term_info
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
            mainlabel = vfbTerm.term.core.label
            if vfbTerm.term.core.symbol and len(vfbTerm.term.core.symbol) > 0:
                meta["Symbol"] = "[%s](%s)"%(vfbTerm.term.core.symbol, vfbTerm.term.core.short_form)
                mainlabel = vfbTerm.term.core.symbol
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
                        if "image_" in key and not ("thumbnail" in key or "folder" in key) and len(vars(image.channel_image.image)[key]) > 1:
                            record[key.replace("image_","")] = vars(image.channel_image.image)[key].replace("http://","https://")
                    images[image.channel_image.image.template_anatomy.short_form].append(record)
                termInfo["Examples"] = images
                # add a query to `queries` list for listing all available images
                queries.append({"query":"ListAllAvailableImages","label":"Find images of %s"%(mainlabel),"function":"get_instances","takes":[{"short_form":{"$and":["Class","Anatomy"]},"default":"%s"%(vfbTerm.term.core.short_form)}]})
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
                            if "image_" in key and not ("thumbnail" in key or "folder" in key) and len(vars(image.image)[key]) > 1:
                                record[key.replace("image_","")] = vars(image.image)[key].replace("http://","https://")
                        images[image.image.template_anatomy.short_form].append(record)
                    # Add the thumbnails to the term info
                    termInfo["Images"] = images

            if contains_all_tags(meta["SuperTypes"],["Individual","Neuron"]):
                queries.append({"query":"SimilarMorphologyTo","label":"Find similar neurons to %s"%(mainlabel),"function":"get_similar_neurons_instances","takes":[{"short_form":{"$and":["Individual","Neuron"]},"default":"%s"%(vfbTerm.term.core.short_form)}]})

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
    pd = pd.DataFrame.from_records(vc.get_instances(short_form, summary=True))
    results = {
        "headers": {
            "label": {"title": "Name", "type": "markdown", "order": 0, "sort": {0: "Asc"}},
            "parent": {"title": "Parent Type", "type": "markdown", "order": 1},
            "template": {"title": "Template", "type": "string", "order": 4},
            "tags": {"title": "Gross Types", "type": "tags", "order": 3},
        },
        "rows": formatDataframe(df).to_dict('records')
    }
    
    return results
    
def get_similar_neurons_instances(short_form: str, similarity_score='NBLAST_score'):
    """
    Retrieves available similar neurons for the given neuron short form.

    :param short_form: short form of the neuron
    :param similarity_score: optionally specify similarity score to choose
    :return: results rows
    """

    df = vc.get_similar_neurons(short_form, similarity_score=similarity_score, return_dataframe=True)

    results = {'headers': 
        {
            'id': {title: 'ID', 'type': 'string', 'hidden': true}, 
            'score': {'title': 'Score', 'type': 'numeric', 'order': 1, 'sort': {0: 'Desc'}},
            'name': {'title': 'Name', 'type': 'markdown', 'order': 1, 'sort': {1: 'Asc'}}, 
            'tags': {'title': 'Tags', 'type': 'tags', 'order': 2},
            'source': {'title': 'Source', 'type': 'metadata', 'order': 3},
            'source_id': {'title': 'Source ID', 'type': 'metadata', 'order': 4},
        }, 
        'rows': formatDataframe(df).to_dict('records')
    }
    


def formatDataframe(df):
    """
    Merge label/id pairs into a markdown link and update column names.
    
    :param df: pandas DataFrame 
    :return: pandas DataFrame with merged label/id pairs in 'label' and 'parent' columns
    """
    # Merge label/id pairs for both label/id and parent_label/parent_id columns
    df['label'] = '[%s](%s)' % (df['label'], df['id'])
    df['parent'] = '[%s](%s)' % (df['parent_label'], df['parent_id'])
    
    # Drop the original label/id and parent_label/parent_id columns
    df.drop(columns=['label', 'id', 'parent_label', 'parent_id'], inplace=True)
    
    # Check tags is a list
    def merge_tags(tags):
        if isinstance(tags, str):
            tags_list = tags.split('|')
            return tags_list
        else:
            return tags

    df['tags'] = df['tags'].apply(merge_tags)
        
    # Return the updated DataFrame
    return df.rename(columns={'datasource': 'source', 'accession': 'source_id'})

    return results

def contains_all_tags(lst: List[str], tags: List[str]) -> bool:
    """
    Checks if the given list contains all the tags passed.

    :param lst: list of strings to check
    :param tags: list of strings to check for in lst
    :return: True if lst contains all tags, False otherwise
    """
    return all(tag in lst for tag in tags)
