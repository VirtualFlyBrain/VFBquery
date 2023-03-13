import pysolr
from term_info_queries import deserialize_term_info
from vfb_connect.cross_server_tools import VfbConnect
from marshmallow import Schema, fields, post_load
from typing import List, Tuple
import pandas as pd

# Connect to the VFB SOLR server
vfb_solr = pysolr.Solr('http://solr.virtualflybrain.org/solr/vfb_json/', always_commit=False, timeout=990)

# Create a VFB connection object for retrieving instances
vc = VfbConnect()

class Query:
    def __init__(self, query, label, function, takes, default):
        self.query = query
        self.label = label 
        self.function = function 
        self.takes = takes 
        self.default = default 

class LogicFormSchema(Schema):
    and_ = fields.List(fields.Nested('self'), attribute='$and', required=False, allow_none=True)
    or_ = fields.List(fields.Nested('self'), attribute='$or', required=False, allow_none=True)
    not_ = fields.Nested('self', attribute='$not', required=False, allow_none=True)

    @post_load
    def deserialize_logic_form(self, data, **kwargs):
        if '!' in data:
            return {"!": data["not_"]}
        elif '&&' in data or '||' in data:
            return {k: v for k, v in data.items() if k in ['&&', '||']}
        else:
            return data

class TakesSchema(Schema):
    short_form = fields.Nested(LogicFormSchema(), required=False, many=True, allow_none=True)
    default = fields.String(required=False, allow_none=True)

class QuerySchema(Schema):
    query = fields.String(required=True)
    label = fields.String(required=True)
    function = fields.String(required=True)
    takes = fields.List(fields.Nested(TakesSchema(), many=True), required=False, allow_none=True)

class Coordinates:
    def __init__(self, X, Y, Z):
        self.X = X
        self.Y = Y
        self.Z = Z

class CoordinatesSchema(Schema):
    X = fields.Float(required=True)
    Y = fields.Float(required=True)
    Z = fields.Float(required=True)
    
    def _serialize(self, obj, **kwargs):
        return {"X": obj.X, "Y": obj.Y, "Z": obj.Z}
    
    def _deserialize(self, value, attr=None, data=None, **kwargs):
        return {"X":value.X, "Y":value.Y, "Z":value.Z}

class CoordinatesField(fields.Nested):
    def __init__(self, **kwargs):
        super().__init__(CoordinatesSchema(), **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return value
        if not isinstance(value, Coordinates):
            raise ValidationError("Invalid input")
        return {"X": value.X, "Y": value.Y, "Z": value.Z}

    def _deserialize(self, value, attr=None, data=None, **kwargs):
        if value is None:
            return value
        return f"X={value.X}, Y={value.Y}, Z={value.Z}" 

class Image:
    def __init__(self, id, label, thumbnail=None, thumbnail_transparent=None, nrrd=None, wlz=None, obj=None, swc=None, index=None, center=None, extent=None, voxel=None, orientation=None, type_id=None, type_label=None):
        self.id = id
        self.label = label
        self.thumbnail = thumbnail
        self.thumbnail_transparent = thumbnail_transparent
        self.nrrd = nrrd
        self.wlz = wlz
        self.obj = obj
        self.swc = swc
        self.index = index
        self.center = center
        self.extent = extent
        self.voxel = voxel
        self.orientation = orientation
        self.type_label = type_label
        self.type_id = type_id

class ImageSchema(Schema):
    id = fields.String(required=True)
    label = fields.String(required=True)
    thumbnail = fields.String(required=False, allow_none=True)
    thumbnail_transparent = fields.String(required=False, allow_none=True)
    nrrd = fields.String(required=False, allow_none=True)
    wlz = fields.String(required=False, allow_none=True)
    obj = fields.String(required=False, allow_none=True)
    swc = fields.String(required=False, allow_none=True)
    index = fields.Integer(required=False, allow_none=True)
    center = fields.Nested(CoordinatesSchema(), required=False, allow_none=True)
    extent = fields.Nested(CoordinatesSchema(), required=False, allow_none=True)
    voxel = fields.Nested(CoordinatesSchema(), required=False, allow_none=True)
    orientation = fields.String(required=False, allow_none=True)
    type_label = fields.String(required=False, allow_none=True)
    type_id = fields.String(required=False, allow_none=True)

class ImageField(fields.Nested):
    def __init__(self, **kwargs):
        super().__init__(ImageSchema(), **kwargs)
    
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return value
        return {"id": value.id
                , "label": value.label
                , "thumbnail": value.thumbnail
                , "thumbnail_transparent": value.thumbnail_transparent
                , "nrrd": value.nrrd
                , "wlz": value.wlz
                , "obj": value.obj
                , "swc": value.swc
                , "index": value.index
                , "center": value.center
                , "extent": value.extent
                , "voxel": value.voxel
                , "orientation": value.orientation
                , "type_id": value.type_id
                , "type_label": value.type_label
                }
      
    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return value
        return ImageSchema().load(value)

class QueryField(fields.Nested):
    def __init__(self, **kwargs):
        super().__init__(QuerySchema, **kwargs)
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return value
        return {"query": value.query
                , "label": value.label
                , "function": value.function
                , "takes": value.takes
                , "default": value.default
                }

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return value
        return QuerySchema().load(value)


class TermInfoOutputSchema(Schema):
    Name = fields.String(required=True)
    Id = fields.String(required=True)
    SuperTypes = fields.List(fields.String(), required=True)
    Meta = fields.Dict(keys=fields.String(), values=fields.String(), required=True)
    Tags = fields.List(fields.String(), required=True)
    Queries = fields.List(fields.Nested(QuerySchema), missing=[], required=False)
    IsIndividual = fields.Bool(missing=False, required=False)
    Images = fields.Dict(keys=fields.String(), values=fields.List(fields.Nested(ImageSchema()), missing={}), required=False, allow_none=True)
    IsClass = fields.Bool(missing=False, required=False)
    Examples = fields.Dict(keys=fields.String(), values=fields.List(fields.Nested(ImageSchema()), missing={}), required=False, allow_none=True)
    IsTemplate = fields.Bool(missing=False, required=False)
    Domains = fields.Dict(keys=fields.Integer(), values=fields.Nested(ImageSchema()), required=False, allow_none=True)

def term_info_parse_object(results, short_form):
    termInfo = {}
    if results.hits > 0 and results.docs and len(results.docs) > 0:
        termInfo["Meta"] = {}
        # Deserialize the term info from the first result
        vfbTerm = deserialize_term_info(results.docs[0]['term_info'][0])
        queries = []
        termInfo["Id"] = vfbTerm.term.core.short_form
        termInfo["Meta"]["Name"] = "[%s](%s)"%(vfbTerm.term.core.label, vfbTerm.term.core.short_form)
        mainlabel = vfbTerm.term.core.label
        if vfbTerm.term.core.symbol and len(vfbTerm.term.core.symbol) > 0:
            meta["Symbol"] = "[%s](%s)"%(vfbTerm.term.core.symbol, vfbTerm.term.core.short_form)
            mainlabel = vfbTerm.term.core.symbol
        termInfo["Name"] = mainlabel
        termInfo["SuperTypes"] = vfbTerm.term.core.types
        if "Class" in termInfo["SuperTypes"]:
            termInfo["IsClass"] = True
        elif "Individual" in termInfo["SuperTypes"]:
            termInfo["IsIndividual"] = True
        try:
            # Retrieve tags from the term's unique_facets attribute
            termInfo["Tags"] = vfbTerm.term.core.unique_facets
        except NameError:
            # If unique_facets attribute doesn't exist, use the term's types
            termInfo["Tags"] = vfbTerm.term.core.types
        try:
            # Retrieve description from the term's description attribute
            termInfo["Meta"]["Description"] = "%s"%("".join(vfbTerm.term.description))
        except NameError:
            pass
        try:
            # Retrieve comment from the term's comment attribute
            termInfo["Meta"]["Comment"] = "%s"%("".join(vfbTerm.term.comment))
        except NameError:
            pass
        except AttributeError:
            print(f"vfbTerm.term.comment: {vfbTerm.term}")

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
            queries.append({"query":"ListAllAvailableImages","label":"List all available images of %s"%(termInfo["Name"]),"function":"get_instances","takes":[{"short_form":{"$and":["Class","Anatomy"]},"default":"%s"%(vfbTerm.term.core.short_form)}]})
            
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
              
        if vfbTerm.template_channel and vfbTerm.template_channel.channel.short_form:
            termInfo["IsTemplate"] = True
            images = {}
            image = vfbTerm.template_channel
            record = {}
            record["id"] = vfbTerm.template_channel.channel.short_form
            label = vfbTerm.template_channel.channel.label
            if vfbTerm.template_channel.channel.symbol != "" and len(vfbTerm.template_channel.channel.symbol) > 0:
                label = vfbTerm.template_channel.channel.symbol
            record["label"] = label
            if not vfbTerm.template_channel.channel.short_form in images.keys():
                images[vfbTerm.template_channel.channel.short_form]=[]
            record["thumbnail"] = image.image_thumbnail.replace("http://","https://").replace("thumbnailT.png","thumbnail.png")
            record["thumbnail_transparent"] = image.image_thumbnail.replace("http://","https://").replace("thumbnail.png","thumbnailT.png")
            for key in vars(image).keys():
                if "image_" in key and not ("thumbnail" in key or "folder" in key) and len(vars(image)[key]) > 1:
                    record[key.replace("image_","")] = vars(image)[key].replace("http://","https://")
            if len(image.index) > 0:
              record[index] = int(image.index[0])
            vars(image).keys()
            image_vars = vars(image)
            if 'center' in image_vars.keys():
                record['center'] = image.get_center()
            if 'extent' in image_vars.keys():
                record['extent'] = image.get_extent()
            if 'voxel' in image_vars.keys():
                record['voxel'] = image.get_voxel()
            if 'orientation' in image_vars.keys():
                record['orientation'] = image.orientation
            images[vfbTerm.template_channel.channel.short_form].append(record)
                
            # Add the thumbnails to the term info
            termInfo["Images"] = images
            
        if vfbTerm.template_domains and len(vfbTerm.template_domains) > 0:
            images = {}
            termInfo["IsTemplate"] = True
            for image in vfbTerm.template_domains:
              record = {}
              record["id"] = image.anatomical_individual.short_form
              label = image.anatomical_individual.label
              if image.anatomical_individual.symbol != "" and len(image.anatomical_individual.symbol) > 0:
                  label = image.anatomical_individual.symbol
              record["label"] = label
              record["type_id"] = image.anatomical_type.short_form
              label = image.anatomical_type.label
              if image.anatomical_type.symbol != "" and len(image.anatomical_type.symbol) > 0:
                  label = image.anatomical_type.symbol
              record["type_label"] = label
              record["index"] = int(image.index[0])
              record["thumbnail"] = image.folder.replace("http://","https://") + "thumbnail.png"
              record["thumbnail_transparent"] = image.folder.replace("http://","https://") + "thumbnailT.png"
              for key in vars(image).keys():
                  if "image_" in key and not ("thumbnail" in key or "folder" in key) and len(vars(image)[key]) > 1:
                      record[key.replace("image_","")] = vars(image)[key].replace("http://","https://")
              record["center"] = image.get_center()
              images[record["index"]] = record
                
            # Add the thumbnails to the term info
            termInfo["Domains"] = images
            
        if contains_all_tags(meta["SuperTypes"],["Individual","Neuron"]):
            queries.append({"query":"SimilarMorphologyTo","label":"Find similar neurons to %s"%(termInfo["Name"]),"function":"get_similar_neurons","takes":[{"short_form":{"$and":["Individual","Neuron"]},"default":"%s"%(vfbTerm.term.core.short_form)}]})

        # Add the queries to the term info
        termInfo["Queries"] = queries
        
        print(termInfo)
 
    return TermInfoOutputSchema().load(termInfo)

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
        return term_info_parse_object(results, short_form)
    except IndexError:
        print(f"No results found for ID '{short_form}'")
        print("Error accessing SOLR server!")   

                
def get_instances(short_form: str):
    """
    Retrieves available instances for the given class short form.

    :param short_form: short form of the class
    :return: results rows
    """
    df = pd.DataFrame.from_records(vc.get_instances(short_form, summary=True))
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
    
def get_similar_neurons(short_form: str, similarity_score='NBLAST_score'):
    """
    Retrieves available similar neurons for the given neuron short form.

    :param short_form: short form of the neuron
    :param similarity_score: optionally specify similarity score to choose
    :return: results rows
    """

    df = vc.get_similar_neurons(short_form, similarity_score=similarity_score, return_dataframe=True)

    results = {'headers': 
        {
            'score': {'title': 'Score', 'type': 'numeric', 'order': 1, 'sort': {0: 'Desc'}},
            'name': {'title': 'Name', 'type': 'markdown', 'order': 1, 'sort': {1: 'Asc'}}, 
            'tags': {'title': 'Tags', 'type': 'tags', 'order': 2},
            'source': {'title': 'Source', 'type': 'metadata', 'order': 3},
            'source_id': {'title': 'Source ID', 'type': 'metadata', 'order': 4},
        }, 
        'rows': formatDataframe(df).to_dict('records')
    }
    
    return results

def formatDataframe(df):
    """
    Merge label/id pairs into a markdown link and update column names.

    :param df: pandas DataFrame 
    :return: pandas DataFrame with merged label/id pairs in 'label' and 'parent' columns
    """
    if 'label' in df.columns and 'id' in df.columns:
        # Merge label/id pairs for both label/id and parent_label/parent_id columns
        df['label'] = '[%s](%s)' % (df['label'], df['id'])
        # Drop the original label/id columns
        df.drop(columns=['id'], inplace=True)
    if 'parent_label' in df.columns and 'parent_id' in df.columns:
        df['parent'] = '[%s](%s)' % (df['parent_label'], df['parent_id'])
        # Drop the original parent_label/parent_id columns
        df.drop(columns=['parent_label', 'parent_id'], inplace=True)
    if 'tags' in df.columns:
        # Check tags is a list
        def merge_tags(tags):
            if isinstance(tags, str):
                tags_list = tags.split('|')
                return tags_list
            else:
                return tags
        df['tags'] = df['tags'].apply(merge_tags)
    # Check if columns exist before renaming them
    if 'datasource' in df.columns:
        df.rename(columns={'datasource': 'source'}, inplace=True)
    if 'accession' in df.columns:
        df.rename(columns={'accession': 'source_id'}, inplace=True)
    # Return the updated DataFrame
    return df

def contains_all_tags(lst: List[str], tags: List[str]) -> bool:
    """
    Checks if the given list contains all the tags passed.

    :param lst: list of strings to check
    :param tags: list of strings to check for in lst
    :return: True if lst contains all tags, False otherwise
    """
    return all(tag in lst for tag in tags)
