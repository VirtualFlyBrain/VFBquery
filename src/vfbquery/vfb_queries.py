import pysolr
from .term_info_queries import deserialize_term_info
from vfb_connect.cross_server_tools import VfbConnect, dict_cursor
from marshmallow import Schema, fields, post_load
from typing import List, Tuple
import pandas as pd
from marshmallow import ValidationError

# Connect to the VFB SOLR server
vfb_solr = pysolr.Solr('http://solr.virtualflybrain.org/solr/vfb_json/', always_commit=False, timeout=990)

# Create a VFB connection object for retrieving instances
vc = VfbConnect()

class Query:
    def __init__(self, query, label, function, takes, preview=0, preview_columns=[],preview_results={}, count=-1):
        self.query = query
        self.label = label 
        self.function = function 
        self.takes = takes
        self.preview = preview
        self.preview_columns = preview_columns
        self.preview_results = preview_results  
        self.count = count

class TakesSchema(Schema):
    short_form = fields.Raw(required=True)
    default = fields.Raw(required=False, allow_none=True)

class QuerySchema(Schema):
    query = fields.String(required=True)
    label = fields.String(required=True)
    function = fields.String(required=True)
    takes = fields.Nested(TakesSchema(), many=True)

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
                , "preview": value.preview
                , "preview_columns": value.preview_columns
                , "preview_results": value.preview_results  
                , "count": value.count
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
    Queries = fields.Raw(required=False) #having issues to serialize  
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
            termInfo["Meta"]["Symbol"] = "[%s](%s)"%(vfbTerm.term.core.symbol, vfbTerm.term.core.short_form)
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
            q = ListAllAvailableImages_to_schemma(termInfo["Name"], {"short_form":vfbTerm.term.core.short_form})
            queries.append(q)
 
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
              record[image.index] = int(image.index[0])
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
            
        if contains_all_tags(termInfo["SuperTypes"],["Individual","Neuron"]):
          q = SimilarMorphologyTo_to_schemma(termInfo["Name"], {"neuron":vfbTerm.term.core.short_form, "similarity_score": "NBLAST_score"})
          queries.append(q)
        # Add the queries to the term info
        termInfo["Queries"] = queries
        
        print(termInfo)
 
    return TermInfoOutputSchema().load(termInfo)

def SimilarMorphologyTo_to_schemma(name, take_default):
  query = {}
  query["query"] = "SimilarMorphologyTo"
  query["label"] = "Find similar neurons to %s"%(name)
  query["function"] = "get_similar_neurons"
  takes = {}
  takes["short_form"] = {}
  takes["short_form"]["$and"] = ["Individual","Neuron"]
  takes["default"] = take_default 
  query["takes"] = takes 
  query["preview"] = 5
  return query 
   
def ListAllAvailableImages_to_schemma(name, take_default):
  query = {}
  query["query"] = "ListAllAvailableImages"
  query["label"] = "List all available images of %s"%(name)
  query["function"] = "get_instances"
  takes = {}
  takes["short_form"] = {}
  takes["short_form"]["$and"] = ["Class","Anatomy"]
  takes["default"] = take_default 
  query["takes"] = takes
  query["preview"] = 0 
  return query 

def get_term_info(short_form: str, preview: bool = False):
    """
    Retrieves the term info for the given term short form.

    :param short_form: short form of the term
    :return: term info
    """
    try:
        # Search for the term in the SOLR server
        results = vfb_solr.search('id:' + short_form)
        # Check if any results were returned
        parsed_object = term_info_parse_object(results, short_form)
        return parsed_object
    except ValidationError as e:
    # handle the validation error
      print("Schemma validation error when parsing response")
    except IndexError:
        print(f"No results found for ID '{short_form}'")
        print("Error accessing SOLR server!")   

                
def get_instances(short_form: str, return_dataframe=True, limit: int = None):
    """
    Retrieves available instances for the given class short form.
    :param short_form: short form of the class
    :param limit: maximum number of results to return (default None, returns all results)
    :return: results rows
    """

    # Define the Cypher query
    query = f"""
    MATCH (i:Individual)-[:INSTANCEOF]->(p:Class {{ short_form: '{short_form}' }}),
          (i)<-[:depicts]-(:Individual)-[:in_register_with]->(:Template)-[:depicts]->(templ:Template),
          (i)-[:has_source]->(ds:DataSet)
    OPTIONAL MATCH (i)-[rx:database_cross_reference]->(site:Site)
    OPTIONAL MATCH (ds)-[:license|licence]->(lic:License)
    RETURN apoc.text.format("[%s](%s)",[COALESCE(i.symbol[0],i.label),i.short_form]) AS label,
       apoc.text.join(i.uniqueFacets, '|') AS tags,
       apoc.text.format("[%s](%s)",[COALESCE(p.symbol[0],p.label),p.short_form]) AS parent,
       REPLACE(apoc.text.format("[%s](%s)",[COALESCE(site.symbol[0],site.label),site.short_form]), '[null](null)', '') AS source,
       REPLACE(apoc.text.format("[%s](%s)",[rx.accession,site.link_base[0] + rx.accession[0]]), '[null](null)', '') AS source_id,
       apoc.text.format("[%s](%s)",[COALESCE(templ.symbol[0],templ.label),templ.short_form]) AS template,
       apoc.text.format("[%s](%s)",[COALESCE(ds.symbol[0],ds.label),ds.short_form]) AS dataset,
       REPLACE(apoc.text.format("[%s](%s)",[COALESCE(lic.symbol[0],lic.label),lic.short_form]), '[null](null)', '') AS license
    """

    if limit is not None:
        query += f" LIMIT {limit}"

    # Run the query using VFB_connect
    results = vc.nc.commit_list([query])

    # Convert the results to a DataFrame
    df = pd.DataFrame.from_records(dict_cursor(results))

    if return_dataframe:
        return df

    # Format the results
    formatted_results = {
        "headers": {
            "label": {"title": "Name", "type": "markdown", "order": 0, "sort": {0: "Asc"}},
            "parent": {"title": "Parent Type", "type": "markdown", "order": 1},
            "template": {"title": "Template", "type": "markdown", "order": 4},
            "tags": {"title": "Gross Types", "type": "tags", "order": 3},
            "source": {"title": "Data Source", "type": "markdown", "order": 5},
            "source_id": {"title": "Data Source", "type": "markdown", "order": 6},
        },
        "rows": df.to_dict('records')
    }

    return formatted_results
    
def get_similar_neurons(self, neuron, similarity_score='NBLAST_score', return_dataframe=True, limit: int = None):
    """Get JSON report of individual neurons similar to input neuron

    :param neuron:
    :param similarity_score: Optionally specify similarity score to chose
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns list of dicts.
    :param limit: maximum number of results to return (default None, returns all results)
    :return: list of similar neurons (id, label, tags, source (db) id, accession_in_source) + similarity score.
    :rtype: pandas.DataFrame or list of dicts

    """
    query = f"""MATCH (c1:Class)<-[:INSTANCEOF]-(n1)-[r:has_similar_morphology_to]-(n2)-[:INSTANCEOF]->(c2:Class) 
                WHERE n1.short_form = '{neuron}'
                WITH c1, n1, r, n2, c2
                OPTIONAL MATCH (n1)-[dbx1:database_cross_reference]->(s1:Site),
                (n2)-[dbx2:database_cross_reference]->(s2:Site)
                WHERE s1.is_data_source and s2.is_data_source and exists(r.{similarity_score})
                RETURN DISTINCT n2.short_form AS id, r.{similarity_score}[0] AS score, n2.label AS label,
                COLLECT(c2.label) AS tags, s2.short_form AS source_id, dbx2.accession[0] AS accession_in_source
                ORDER BY score DESC"""

    if limit is not None:
        query += f" LIMIT {limit}"

    dc = self.neo_query_wrapper._query(query)
    df = pd.DataFrame.from_records(dc)

    # Rename columns to match the original function
    df = df.rename(columns={
        'id': 'name',
        'label': 'label',
        'tags': 'tags',
        'source_id': 'source',
        'accession_in_source': 'source_id',
    })

    formatted_results = {
        'headers': {
            'score': {'title': 'Score', 'type': 'numeric', 'order': 1, 'sort': {0: 'Desc'}},
            'name': {'title': 'Name', 'type': 'markdown', 'order': 1, 'sort': {1: 'Asc'}},
            'tags': {'title': 'Tags', 'type': 'tags', 'order': 2},
            'source': {'title': 'Source', 'type': 'metadata', 'order': 3},
            'source_id': {'title': 'Source ID', 'type': 'metadata', 'order': 4},
        },
        'rows': formatDataframe(df).to_dict('records')
    }

    if return_dataframe:
        return pd.DataFrame(formatted_results['rows'])
    else:
        return formatted_results

def contains_all_tags(lst: List[str], tags: List[str]) -> bool:
    """
    Checks if the given list contains all the tags passed.

    :param lst: list of strings to check
    :param tags: list of strings to check for in lst
    :return: True if lst contains all tags, False otherwise
    """
    return all(tag in lst for tag in tags)

def fill_query_previews(term_info):
    for query in term_info['Queries']:
        if query.preview > 0:
            function = globals().get(query.function)
            if function:
                # Modify this line to use the correct arguments
                result = function(query.takes["default"], return_dataframe=False, limit=query.preview)
                
                # Filter columns based on preview_columns
                filtered_result = []
                for item in result:
                    filtered_item = {col: item[col] for col in query.preview_columns}
                    filtered_result.append(filtered_item)
                
                query.preview_results = filtered_result
            else:
                print(f"Function {query.function} not found")

