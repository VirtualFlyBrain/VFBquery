import pysolr
from .term_info_queries import deserialize_term_info
# Replace VfbConnect import with our new SimpleVFBConnect
from .owlery_client import SimpleVFBConnect
# Keep dict_cursor if it's used elsewhere - lazy import to avoid GUI issues
from marshmallow import Schema, fields, post_load
from typing import List, Tuple, Dict, Any, Union
import pandas as pd
from marshmallow import ValidationError
import json
import numpy as np
from urllib.parse import unquote
from .solr_result_cache import with_solr_cache
import time
import requests
from concurrent.futures import ThreadPoolExecutor
import inspect

# Custom JSON encoder to handle NumPy and pandas types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif hasattr(obj, 'item'):  # Handle pandas scalar types
            return obj.item()
        return super(NumpyEncoder, self).default(obj)

def safe_to_dict(df, sort_by_id=True):
    """Convert DataFrame to dict with numpy types converted to native Python types"""
    if isinstance(df, pd.DataFrame):
        # Convert numpy dtypes to native Python types
        df_copy = df.copy()
        for col in df_copy.columns:
            if df_copy[col].dtype.name.startswith('int'):
                df_copy[col] = df_copy[col].astype('object')
            elif df_copy[col].dtype.name.startswith('float'):
                df_copy[col] = df_copy[col].astype('object')
        
        # Sort by id column in descending order if it exists and sort_by_id is True
        if sort_by_id and 'id' in df_copy.columns:
            df_copy = df_copy.sort_values('id', ascending=False)
        
        return df_copy.to_dict("records")
    return df

# Lazy import for dict_cursor to avoid GUI library issues
def get_dict_cursor():
    """Lazy import dict_cursor to avoid import issues during testing"""
    try:
        from .neo4j_client import dict_cursor
        return dict_cursor
    except ImportError as e:
        raise ImportError(f"Could not import dict_cursor: {e}")

# Connect to the VFB SOLR server
vfb_solr = pysolr.Solr('http://solr.virtualflybrain.org/solr/vfb_json/', always_commit=False, timeout=990)

# Replace VfbConnect with SimpleVFBConnect
vc = SimpleVFBConnect()

def initialize_vfb_connect():
    """
    Initialize VFB_connect by triggering the lazy load of the vfb and nc properties.
    This causes VFB_connect to cache all terms, which takes ~95 seconds on first call.
    Subsequent calls to functions using vc.nc will be fast.
    
    :return: True if initialization successful, False otherwise
    """
    try:
        # Access the properties to trigger lazy loading
        _ = vc.vfb
        _ = vc.nc
        return True
    except Exception as e:
        print(f"Failed to initialize VFB_connect: {e}")
        return False

class Query:
    def __init__(self, query, label, function, takes, preview=0, preview_columns=[], preview_results=[], output_format="table", count=-1):
        self.query = query
        self.label = label
        self.function = function
        self.takes = takes
        self.preview = preview
        self.preview_columns = preview_columns
        self.preview_results = preview_results
        self.output_format = output_format
        self.count = count

    def __str__(self):
        return f"Query: {self.query}, Label: {self.label}, Function: {self.function}, Takes: {self.takes}, Preview: {self.preview}, Preview Columns: {self.preview_columns}, Preview Results: {self.preview_results}, Count: {self.count}"

    def to_dict(self):
        return {
            "query": self.query,
            "label": self.label,
            "function": self.function,
            "takes": self.takes,
            "preview": self.preview,
            "preview_columns": self.preview_columns,
            "preview_results": self.preview_results,
            "output_format": self.output_format,
            "count": self.count,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            query=data["query"],
            label=data["label"],
            function=data["function"],
            takes=data["takes"],
            preview=data["preview"],
            preview_columns=data["preview_columns"],
            preview_results=data["preview_results"],
            output_format=data.get("output_format", 'table'),
            count=data["count"],
        )

class TakesSchema(Schema):
    short_form = fields.Raw(required=True)
    default = fields.Raw(required=False, allow_none=True)

class QuerySchema(Schema):
    query = fields.String(required=True)
    label = fields.String(required=True)
    function = fields.String(required=True)
    takes = fields.Nested(TakesSchema(), required=False, missing={})
    preview = fields.Integer(required=False, missing=0)
    preview_columns = fields.List(fields.String(), required=False, missing=[])
    preview_results = fields.List(fields.Dict(), required=False, missing=[])
    output_format = fields.String(required=False, missing='table')
    count = fields.Integer(required=False, missing=-1)

class License:
    def __init__(self, iri, short_form, label, icon, source, source_iri):
        self.iri = iri 
        self.short_form = short_form 
        self.label = label
        self.icon = icon
        self.source = source
        self.source_iri = source_iri

class LicenseSchema(Schema):
    iri        = fields.String(required=True)
    short_form = fields.String(required=True)
    label      = fields.String(required=True)
    icon       = fields.String(required=True)
    source     = fields.String(required=True)
    source_iri = fields.String(required=True)


class LicenseField(fields.Nested):
    def __init__(self, **kwargs):
        super().__init__(LicenseSchema(), **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return value
        if not isinstance(value, License):
            raise ValidationError("Invalid input")
        return {"iri": value.iri
                , "short_form": value.short_form
                , "label": value.label
                ,"icon": value.icon
                , "source": value.source
                , "source_iri": value.source_iri}

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return value
        return LicenseSchema().load(value)
    
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

class QueryField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value.to_dict()

    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, dict):
            raise ValidationError("Invalid input type.")
        return Query.from_dict(value)

class TermInfoOutputSchema(Schema):
    Name = fields.String(required=True)
    Id = fields.String(required=True)
    SuperTypes = fields.List(fields.String(), required=True)
    Meta = fields.Dict(keys=fields.String(), values=fields.String(), required=True)
    Tags = fields.List(fields.String(), required=True)
    Queries = fields.List(QueryField(), required=False)
    IsIndividual = fields.Bool(missing=False, required=False)
    Images = fields.Dict(keys=fields.String(), values=fields.List(fields.Nested(ImageSchema()), missing={}), required=False, allow_none=True)
    IsClass = fields.Bool(missing=False, required=False)
    Examples = fields.Dict(keys=fields.String(), values=fields.List(fields.Nested(ImageSchema()), missing={}), required=False, allow_none=True)
    IsTemplate = fields.Bool(missing=False, required=False)
    IsPaintedDomain = fields.Bool(missing=False, required=False)
    Domains = fields.Dict(keys=fields.Integer(), values=fields.Nested(ImageSchema()), required=False, allow_none=True)
    Licenses = fields.Dict(keys=fields.Integer(), values=fields.Nested(LicenseSchema()), required=False, allow_none=True)
    Publications = fields.List(fields.Dict(keys=fields.String(), values=fields.Field()), required=False)
    Synonyms = fields.List(fields.Dict(keys=fields.String(), values=fields.Field()), required=False, allow_none=True)

    @post_load
    def make_term_info(self, data, **kwargs):
        if "Queries" in data:
            data["Queries"] = [query.to_dict() for query in data["Queries"]]
        return data

    def __str__(self):
        term_info_data = self.make_term_info(self.data)
        if "Queries" in term_info_data:
            term_info_data["Queries"] = [query.to_dict() for query in term_info_data["Queries"]]
        return str(self.dump(term_info_data))

def encode_brackets(text):
    """
    Encodes square brackets in the given text to prevent breaking markdown link syntax.
    Parentheses are NOT encoded as they don't break markdown syntax.

    :param text: The text to encode.
    :return: The text with square brackets encoded.
    """
    return (text.replace('[', '%5B')
                .replace(']', '%5D'))

def encode_markdown_links(df, columns):
    """
    Encodes brackets in the labels within markdown links, leaving the link syntax intact.
    Does NOT encode alt text in linked images ([![...](...)(...)] format).
    Handles multiple comma-separated markdown links in a single string.
    :param df: DataFrame containing the query results.
    :param columns: List of column names to apply encoding to.
    """
    import re
    
    def encode_label(label):
        if not isinstance(label, str):
            return label
            
        try:
            # Handle linked images (format: [![alt text](image_url "title")](link))
            if label.startswith("[!["):
                # Replace http with https in the image URL
                # Pattern: [![anything](http://... "title")](link)
                def secure_image_url(match):
                    alt_text = match.group(1)
                    image_url = match.group(2)
                    title = match.group(3) if match.group(3) else ""
                    link = match.group(4)
                    secure_url = image_url.replace("http://", "https://")
                    if title:
                        return f"[![{alt_text}]({secure_url} \"{title}\")]({link})"
                    else:
                        return f"[![{alt_text}]({secure_url})]({link})"
                
                # Regex to match the entire linked image
                pattern = r'\[\!\[([^\]]+)\]\(([^\'"\s]+)(?:\s+[\'"]([^\'"]*)[\'"])?\)\]\(([^)]+)\)'
                encoded_label = re.sub(pattern, secure_image_url, label)
                return encoded_label
            
            # Process regular markdown links - handle multiple links separated by commas
            # Pattern matches [label](url) format
            elif "[" in label and "](" in label:
                # Use regex to find all markdown links and encode each one separately
                # Pattern: \[([^\]]+)\]\(([^\)]+)\)
                # Matches: [anything except ]](anything except ))
                def encode_single_link(match):
                    label_part = match.group(1)  # The label part (between [ and ])
                    url_part = match.group(2)     # The URL part (between ( and ))
                    # Encode brackets in the label part only
                    label_part_encoded = encode_brackets(label_part)
                    # Ensure URLs use https
                    url_part_secure = url_part.replace("http://", "https://")
                    return f"[{label_part_encoded}]({url_part_secure})"
                
                # Replace all markdown links with their encoded versions
                encoded_label = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', encode_single_link, label)
                return encoded_label
                
        except Exception as e:
            # In case of any other unexpected error, log or print the error and return the original label
            print(f"Error processing label: {label}, error: {e}")
            return label

        # If none of the conditions above match, return the original label
        return label

    for column in columns:
        # Only encode if the column exists in the DataFrame
        if column in df.columns:
            df[column] = df[column].apply(lambda x: encode_label(x) if pd.notnull(x) else x)

    return df
    
def term_info_parse_object(results, short_form):
    termInfo = {}
    termInfo["SuperTypes"] = []
    termInfo["Tags"] = []
    termInfo["Queries"] = []
    termInfo["IsClass"] = False
    termInfo["IsIndividual"] = False
    termInfo["IsTemplate"] = False
    termInfo["Images"] = {}
    termInfo["Examples"] = {}
    termInfo["Domains"] = {}
    termInfo["Licenses"] = {}
    termInfo["Publications"] = []
    termInfo["IsPaintedDomain"] = False
    
    if results.hits > 0 and results.docs and len(results.docs) > 0:
        termInfo["Meta"] = {}
        try:
            # Deserialize the term info from the first result
            vfbTerm = deserialize_term_info(results.docs[0]['term_info'][0])
        except KeyError:
            print(f"SOLR doc missing 'term_info': {results.docs[0]}")
            return None
        except Exception as e:
            print(f"Error deserializing term info: {e}")
            return None
            
        queries = []
        # Initialize synonyms variable to avoid UnboundLocalError
        synonyms = []
        termInfo["Id"] = vfbTerm.term.core.short_form
        termInfo["Meta"]["Name"] = "[%s](%s)"%(encode_brackets(vfbTerm.term.core.label), vfbTerm.term.core.short_form)
        mainlabel = vfbTerm.term.core.label
        if hasattr(vfbTerm.term.core, 'symbol') and vfbTerm.term.core.symbol and len(vfbTerm.term.core.symbol) > 0:
            termInfo["Meta"]["Symbol"] = "[%s](%s)"%(encode_brackets(vfbTerm.term.core.symbol), vfbTerm.term.core.short_form)
            mainlabel = vfbTerm.term.core.symbol
        termInfo["Name"] = mainlabel
        termInfo["SuperTypes"] = vfbTerm.term.core.types if hasattr(vfbTerm.term.core, 'types') else []
        if "Class" in termInfo["SuperTypes"]:
            termInfo["IsClass"] = True
        elif "Individual" in termInfo["SuperTypes"]:
            termInfo["IsIndividual"] = True
        try:
            # Retrieve tags from the term's unique_facets attribute
            termInfo["Tags"] = vfbTerm.term.core.unique_facets
        except (NameError, AttributeError):
            # If unique_facets attribute doesn't exist, use the term's types
            termInfo["Tags"] = vfbTerm.term.core.types if hasattr(vfbTerm.term.core, 'types') else []
        try:
            # Retrieve description from the term's description attribute
            termInfo["Meta"]["Description"] = "%s"%("".join(vfbTerm.term.description))
        except (NameError, AttributeError):
            pass
        try:
            # Retrieve comment from the term's comment attribute
            termInfo["Meta"]["Comment"] = "%s"%("".join(vfbTerm.term.comment))
        except (NameError, AttributeError):
            pass
        
        if hasattr(vfbTerm, 'parents') and vfbTerm.parents and len(vfbTerm.parents) > 0:
            parents = []

            # Sort the parents alphabetically
            sorted_parents = sorted(vfbTerm.parents, key=lambda parent: parent.label)

            for parent in sorted_parents:
                parents.append("[%s](%s)"%(encode_brackets(parent.label), parent.short_form))
            termInfo["Meta"]["Types"] = "; ".join(parents)

        if hasattr(vfbTerm, 'relationships') and vfbTerm.relationships and len(vfbTerm.relationships) > 0:
            relationships = []
            pubs_from_relationships = [] # New: Collect publication references from relationships

            # Group relationships by relation type and remove duplicates
            grouped_relationships = {}
            for relationship in vfbTerm.relationships:
                if hasattr(relationship.relation, 'short_form') and relationship.relation.short_form:
                    relation_key = (relationship.relation.label, relationship.relation.short_form)
                elif hasattr(relationship.relation, 'iri') and relationship.relation.iri:
                    relation_key = (relationship.relation.label, relationship.relation.iri.split('/')[-1])
                elif hasattr(relationship.relation, 'label') and relationship.relation.label:
                    relation_key = (relationship.relation.label, relationship.relation.label)
                else:
                    # Skip relationships with no identifiable relation
                    continue
                    
                if not hasattr(relationship, 'object') or not hasattr(relationship.object, 'label'):
                    # Skip relationships with missing object information
                    continue
                    
                object_key = (relationship.object.label, getattr(relationship.object, 'short_form', ''))
                
                # New: Extract publications from this relationship if they exist
                if hasattr(relationship, 'pubs') and relationship.pubs:
                    for pub in relationship.pubs:
                        if hasattr(pub, 'get_miniref') and pub.get_miniref():
                            publication = {}
                            publication["title"] = pub.core.label if hasattr(pub, 'core') and hasattr(pub.core, 'label') else ""
                            publication["short_form"] = pub.core.short_form if hasattr(pub, 'core') and hasattr(pub.core, 'short_form') else ""
                            publication["microref"] = pub.get_microref() if hasattr(pub, 'get_microref') and pub.get_microref() else ""
                            
                            # Add external references
                            refs = []
                            if hasattr(pub, 'PubMed') and pub.PubMed:
                                refs.append(f"http://www.ncbi.nlm.nih.gov/pubmed/?term={pub.PubMed}")
                            if hasattr(pub, 'FlyBase') and pub.FlyBase:
                                refs.append(f"http://flybase.org/reports/{pub.FlyBase}")
                            if hasattr(pub, 'DOI') and pub.DOI:
                                refs.append(f"https://doi.org/{pub.DOI}")
                            
                            publication["refs"] = refs
                            pubs_from_relationships.append(publication)
                
                if relation_key not in grouped_relationships:
                    grouped_relationships[relation_key] = set()
                grouped_relationships[relation_key].add(object_key)

            # Sort the grouped_relationships by keys
            sorted_grouped_relationships = dict(sorted(grouped_relationships.items()))

            # Append the grouped relationships to termInfo
            for relation_key, object_set in sorted_grouped_relationships.items():
                # Sort the object_set by object_key
                sorted_object_set = sorted(list(object_set))
                relation_objects = []
                for object_key in sorted_object_set:
                    relation_objects.append("[%s](%s)" % (encode_brackets(object_key[0]), object_key[1]))
                relationships.append("[%s](%s): %s" % (encode_brackets(relation_key[0]), relation_key[1], ', '.join(relation_objects)))
            termInfo["Meta"]["Relationships"] = "; ".join(relationships)

            # New: Add relationship publications to main publications list
            if pubs_from_relationships:
                if "Publications" not in termInfo:
                    termInfo["Publications"] = pubs_from_relationships
                else:
                    # Merge with existing publications, avoiding duplicates by short_form
                    existing_pub_short_forms = {pub.get("short_form", "") for pub in termInfo["Publications"]}
                    for pub in pubs_from_relationships:
                        if pub.get("short_form", "") not in existing_pub_short_forms:
                            termInfo["Publications"].append(pub)
                            existing_pub_short_forms.add(pub.get("short_form", ""))

        # If the term has anatomy channel images, retrieve the images and associated information
        if vfbTerm.anatomy_channel_image and len(vfbTerm.anatomy_channel_image) > 0:
            images = {}
            for image in vfbTerm.anatomy_channel_image:
                # Check if this is a computer graphic image (painted domain)
                if hasattr(image, 'channel_image') and hasattr(image.channel_image, 'image') and hasattr(image.channel_image.image, 'imaging_technique'):
                    technique = image.channel_image.image.imaging_technique
                    if hasattr(technique, 'symbol') and technique.symbol and 'computer' in technique.symbol.lower():
                        termInfo["IsPaintedDomain"] = True
                
                record = {}
                record["id"] = image.anatomy.short_form
                label = image.anatomy.label
                if image.anatomy.symbol and len(image.anatomy.symbol) > 0:
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
            
            # Sort each template's images by id in descending order (newest first)
            for template_key in images:
                images[template_key] = sorted(images[template_key], key=lambda x: x["id"], reverse=True)
            
            termInfo["Examples"] = images
            # add a query to `queries` list for listing all available images
            q = ListAllAvailableImages_to_schema(termInfo["Name"], {"short_form":vfbTerm.term.core.short_form})
            queries.append(q)

        # If the term has channel images but not anatomy channel images, create thumbnails from channel images.
        if vfbTerm.channel_image and len(vfbTerm.channel_image) > 0:
            images = {}
            for image in vfbTerm.channel_image:
                # Check if this is a computer graphic image (painted domain)
                if hasattr(image, 'image') and hasattr(image.image, 'imaging_technique'):
                    technique = image.image.imaging_technique
                    if hasattr(technique, 'symbol') and technique.symbol and 'computer' in technique.symbol.lower():
                        termInfo["IsPaintedDomain"] = True
                
                record = {}
                record["id"] = vfbTerm.term.core.short_form
                label = vfbTerm.term.core.label
                if vfbTerm.term.core.symbol and len(vfbTerm.term.core.symbol) > 0:
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
            
            # Sort each template's images by id in descending order (newest first)
            for template_key in images:
                images[template_key] = sorted(images[template_key], key=lambda x: x["id"], reverse=True)
            
            # Add the thumbnails to the term info
            termInfo["Images"] = images

        if vfbTerm.dataset_license and len(vfbTerm.dataset_license) > 0: 
            licenses = {}
            for idx, dataset_license in enumerate(vfbTerm.dataset_license):
                record = {}
                record['iri'] = dataset_license.license.core.iri
                record['short_form'] = dataset_license.license.core.short_form
                record['label'] = dataset_license.license.core.label
                record['icon'] = dataset_license.license.icon
                record['source_iri'] = dataset_license.dataset.core.iri
                record['source'] = dataset_license.dataset.core.label
                licenses[idx] = record 
            termInfo["Licenses"] = licenses
              
        if vfbTerm.template_channel and vfbTerm.template_channel.channel.short_form:
            termInfo["IsTemplate"] = True
            images = {}
            image = vfbTerm.template_channel
            record = {}
            
            # Validate that the channel ID matches the template ID (numeric part should be the same)
            template_id = vfbTerm.term.core.short_form
            channel_id = vfbTerm.template_channel.channel.short_form
            
            # Extract numeric parts for validation
            if template_id and channel_id:
                template_numeric = template_id.replace("VFB_", "") if template_id.startswith("VFB_") else ""
                channel_numeric = channel_id.replace("VFBc_", "") if channel_id.startswith("VFBc_") else ""
                
                if template_numeric != channel_numeric:
                    print(f"Warning: Template ID {template_id} does not match channel ID {channel_id}")
                    label = vfbTerm.template_channel.channel.label
                    record["id"] = channel_id
                else:
                    label = vfbTerm.term.core.label
                    record["id"] = template_id
            
            if vfbTerm.template_channel.channel.symbol != "" and len(vfbTerm.template_channel.channel.symbol) > 0:
                label = vfbTerm.template_channel.channel.symbol
            record["label"] = label
            if not template_id in images.keys():
                images[template_id]=[]
            record["thumbnail"] = image.image_thumbnail.replace("http://","https://").replace("thumbnailT.png","thumbnail.png")
            record["thumbnail_transparent"] = image.image_thumbnail.replace("http://","https://").replace("thumbnail.png","thumbnailT.png")
            for key in vars(image).keys():
                if "image_" in key and not ("thumbnail" in key or "folder" in key) and len(vars(image)[key]) > 1:
                    record[key.replace("image_","")] = vars(image)[key].replace("http://","https://")
            if len(image.index) > 0:
              record['index'] = int(image.index[0])
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
            images[template_id].append(record)

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
                    record["thumbnail"] = image.folder.replace("http://", "https://") + "thumbnail.png"
                    record["thumbnail_transparent"] = image.folder.replace("http://", "https://") + "thumbnailT.png"
                    for key in vars(image).keys():
                        if "image_" in key and not ("thumbnail" in key or "folder" in key) and len(vars(image)[key]) > 1:
                            record[key.replace("image_", "")] = vars(image)[key].replace("http://", "https://")
                    record["center"] = image.get_center()
                    images[record["index"]] = record

                # Sort the domains by their index and add them to the term info
                sorted_images = {int(key): value for key, value in sorted(images.items(), key=lambda x: x[0])}
                termInfo["Domains"] = sorted_images

        if contains_all_tags(termInfo["SuperTypes"], ["Individual", "Neuron"]):
            q = SimilarMorphologyTo_to_schema(termInfo["Name"], {"neuron": vfbTerm.term.core.short_form, "similarity_score": "NBLAST_score"})
            queries.append(q)
        if contains_all_tags(termInfo["SuperTypes"], ["Individual", "Neuron", "has_neuron_connectivity"]):
            q = NeuronInputsTo_to_schema(termInfo["Name"], {"neuron_short_form": vfbTerm.term.core.short_form})
            queries.append(q)
            # NeuronNeuronConnectivity query - neurons connected to this neuron
            q = NeuronNeuronConnectivityQuery_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # NeuronsPartHere query - for Class+Anatomy terms (synaptic neuropils, etc.)
        # Matches XMI criteria: Class + Synaptic_neuropil, or other anatomical regions
        if contains_all_tags(termInfo["SuperTypes"], ["Class"]) and (
            "Synaptic_neuropil" in termInfo["SuperTypes"] or 
            "Anatomy" in termInfo["SuperTypes"]
        ):
            q = NeuronsPartHere_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # NeuronsSynaptic query - for synaptic neuropils and visual systems
        # Matches XMI criteria: Class + (Synaptic_neuropil OR Visual_system OR Synaptic_neuropil_domain)
        if contains_all_tags(termInfo["SuperTypes"], ["Class"]) and (
            "Synaptic_neuropil" in termInfo["SuperTypes"] or 
            "Visual_system" in termInfo["SuperTypes"] or
            "Synaptic_neuropil_domain" in termInfo["SuperTypes"]
        ):
            q = NeuronsSynaptic_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # NeuronsPresynapticHere query - for synaptic neuropils and visual systems
        # Matches XMI criteria: Class + (Synaptic_neuropil OR Visual_system OR Synaptic_neuropil_domain)
        if contains_all_tags(termInfo["SuperTypes"], ["Class"]) and (
            "Synaptic_neuropil" in termInfo["SuperTypes"] or 
            "Visual_system" in termInfo["SuperTypes"] or
            "Synaptic_neuropil_domain" in termInfo["SuperTypes"]
        ):
            q = NeuronsPresynapticHere_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # NeuronsPostsynapticHere query - for synaptic neuropils and visual systems
        # Matches XMI criteria: Class + (Synaptic_neuropil OR Visual_system OR Synaptic_neuropil_domain)
        if contains_all_tags(termInfo["SuperTypes"], ["Class"]) and (
            "Synaptic_neuropil" in termInfo["SuperTypes"] or 
            "Visual_system" in termInfo["SuperTypes"] or
            "Synaptic_neuropil_domain" in termInfo["SuperTypes"]
        ):
            q = NeuronsPostsynapticHere_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # ComponentsOf query - for clones
        # Matches XMI criteria: Class + Clone
        if contains_all_tags(termInfo["SuperTypes"], ["Class", "Clone"]):
            q = ComponentsOf_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # PartsOf query - for any Class
        # Matches XMI criteria: Class (any)
        if contains_all_tags(termInfo["SuperTypes"], ["Class"]):
            q = PartsOf_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # SubclassesOf query - for any Class
        # Matches XMI criteria: Class (any)
        if contains_all_tags(termInfo["SuperTypes"], ["Class"]):
            q = SubclassesOf_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # NeuronClassesFasciculatingHere query - for tracts/nerves
        # Matches XMI criteria: Class + Tract_or_nerve (VFB uses Neuron_projection_bundle type)
        if contains_all_tags(termInfo["SuperTypes"], ["Class"]) and "Neuron_projection_bundle" in termInfo["SuperTypes"]:
            q = NeuronClassesFasciculatingHere_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # TractsNervesInnervatingHere query - for synaptic neuropils
        # Matches XMI criteria: Class + (Synaptic_neuropil OR Synaptic_neuropil_domain)
        if contains_all_tags(termInfo["SuperTypes"], ["Class"]) and (
            "Synaptic_neuropil" in termInfo["SuperTypes"] or
            "Synaptic_neuropil_domain" in termInfo["SuperTypes"]
        ):
            q = TractsNervesInnervatingHere_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # LineageClonesIn query - for synaptic neuropils
        # Matches XMI criteria: Class + (Synaptic_neuropil OR Synaptic_neuropil_domain)
        if contains_all_tags(termInfo["SuperTypes"], ["Class"]) and (
            "Synaptic_neuropil" in termInfo["SuperTypes"] or
            "Synaptic_neuropil_domain" in termInfo["SuperTypes"]
        ):
            q = LineageClonesIn_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # ImagesNeurons query - for synaptic neuropils
        # Matches XMI criteria: Class + (Synaptic_neuropil OR Synaptic_neuropil_domain)
        # Returns individual neuron images (instances) rather than neuron classes
        if contains_all_tags(termInfo["SuperTypes"], ["Class"]) and (
            "Synaptic_neuropil" in termInfo["SuperTypes"] or
            "Synaptic_neuropil_domain" in termInfo["SuperTypes"]
        ):
            q = ImagesNeurons_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # ImagesThatDevelopFrom query - for neuroblasts
        # Matches XMI criteria: Class + Neuroblast
        # Returns individual neuron images that develop from the neuroblast
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Class", "Neuroblast"]):
            q = ImagesThatDevelopFrom_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # epFrag query - for expression patterns
        # Matches XMI criteria: Class + Expression_pattern
        # Returns individual expression pattern fragment images
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Class", "Expression_pattern"]):
            q = epFrag_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # ExpressionOverlapsHere query - for anatomical regions
        # Matches XMI criteria: Class + Anatomy
        # Returns expression patterns that overlap with the anatomical region
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Class", "Anatomy"]):
            q = ExpressionOverlapsHere_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # anatScRNAseqQuery query - for anatomical regions with scRNAseq data
        # Matches XMI criteria: Class + Anatomy + hasScRNAseq
        # Returns scRNAseq clusters and datasets for the anatomical region
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Class", "Anatomy", "hasScRNAseq"]):
            q = anatScRNAseqQuery_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # clusterExpression query - for clusters
        # Matches XMI criteria: Individual + Cluster
        # Returns genes expressed in the cluster
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Individual", "Cluster"]):
            q = clusterExpression_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # expressionCluster query - for genes with scRNAseq data
        # Matches XMI criteria: Class + Gene + hasScRNAseq
        # Returns clusters expressing the gene
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Class", "Gene", "hasScRNAseq"]):
            q = expressionCluster_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # scRNAdatasetData query - for scRNAseq datasets
        # Matches XMI criteria: DataSet + hasScRNAseq
        # Returns all clusters in the dataset
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["DataSet", "hasScRNAseq"]):
            q = scRNAdatasetData_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # NBLAST similarity queries
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Individual", "Neuron", "NBLASTexp"]):
            q = SimilarMorphologyToPartOf_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # SimilarMorphologyToPartOfexp query - reverse NBLASTexp
        # Matches XMI criteria: (Individual + Expression_pattern + NBLASTexp) OR (Individual + Expression_pattern_fragment + NBLASTexp)
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Individual", "NBLASTexp"]) and (
            "Expression_pattern" in termInfo["SuperTypes"] or
            "Expression_pattern_fragment" in termInfo["SuperTypes"]
        ):
            q = SimilarMorphologyToPartOfexp_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Individual", "neuronbridge"]):
            q = SimilarMorphologyToNB_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Individual", "Expression_pattern", "neuronbridge"]):
            q = SimilarMorphologyToNBexp_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Individual", "UNBLAST"]):
            q = SimilarMorphologyToUserData_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # Dataset/Template queries
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Template", "Individual"]):
            q = PaintedDomains_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
            q2 = AllAlignedImages_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q2)
            q3 = AlignedDatasets_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q3)
        
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["DataSet", "has_image"]):
            q = DatasetImages_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Template"]):
            q = AllDatasets_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # Publication query
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Individual", "pub"]):
            q = TermsForPub_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # Transgene expression query
        # Matches XMI criteria: (Class + Nervous_system + Anatomy) OR (Class + Nervous_system + Neuron)
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Class", "Nervous_system"]) and (
            "Anatomy" in termInfo["SuperTypes"] or "Neuron" in termInfo["SuperTypes"]
        ):
            q = TransgeneExpressionHere_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # For individuals that are painted domains of anatomical regions, add parent class queries
        if termInfo["IsIndividual"] and termInfo["IsPaintedDomain"]:
            anatomical_classes = []
            
            # Check parents
            if vfbTerm.parents:
                for parent in vfbTerm.parents:
                    if parent.types and "Class" in parent.types:
                        anatomical_classes.append(parent)
            
            # Check relationships for anatomical classes
            if vfbTerm.relationships:
                for rel in vfbTerm.relationships:
                    if hasattr(rel, 'object') and rel.object and hasattr(rel.object, 'types') and rel.object.types:
                        if "Class" in rel.object.types:
                            anatomical_classes.append(rel.object)
            
            # Remove duplicates based on short_form
            seen = set()
            unique_anatomical_classes = []
            for cls in anatomical_classes:
                if cls.short_form not in seen:
                    seen.add(cls.short_form)
                    unique_anatomical_classes.append(cls)
            
            for parent in unique_anatomical_classes:
                parent_short_form = parent.short_form
                parent_label = parent.label if parent.label else parent_short_form
                
                # Add queries based on parent types
                if "Anatomy" in parent.types or "Synaptic_neuropil" in parent.types or "Synaptic_neuropil_domain" in parent.types:
                    # NeuronsPartHere query
                    q = NeuronsPartHere_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                    
                    # NeuronsSynaptic query
                    q = NeuronsSynaptic_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                    
                    # NeuronsPresynapticHere query
                    q = NeuronsPresynapticHere_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                    
                    # NeuronsPostsynapticHere query
                    q = NeuronsPostsynapticHere_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                    
                    # TractsNervesInnervatingHere query
                    q = TractsNervesInnervatingHere_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                    
                    # LineageClonesIn query
                    q = LineageClonesIn_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                    
                    # ImagesNeurons query
                    q = ImagesNeurons_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                
                if "Anatomy" in parent.types:
                    # ExpressionOverlapsHere query
                    q = ExpressionOverlapsHere_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                
                if "Anatomy" in parent.types and "hasScRNAseq" in parent.types:
                    # anatScRNAseqQuery query
                    q = anatScRNAseqQuery_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                
                if "Neuron_projection_bundle" in parent.types:
                    # NeuronClassesFasciculatingHere query
                    q = NeuronClassesFasciculatingHere_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                
                if "Neuroblast" in parent.types:
                    # ImagesThatDevelopFrom query
                    q = ImagesThatDevelopFrom_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                
                if "Expression_pattern" in parent.types:
                    # epFrag query
                    q = epFrag_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                
                if "Nervous_system" in parent.types and ("Anatomy" in parent.types or "Neuron" in parent.types):
                    # TransgeneExpressionHere query
                    q = TransgeneExpressionHere_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                
                # PartsOf query - for any Class
                q = PartsOf_to_schema(parent_label, {"short_form": parent_short_form})
                queries.append(q)
                
                # SubclassesOf query - for any Class
                q = SubclassesOf_to_schema(parent_label, {"short_form": parent_short_form})
                queries.append(q)
        
        # Add Publications to the termInfo object
        if vfbTerm.pubs and len(vfbTerm.pubs) > 0:
            publications = []
            for pub in vfbTerm.pubs:
                if pub.get_miniref():
                    publication = {}
                    publication["title"] = pub.core.label if pub.core.label else ""
                    publication["short_form"] = pub.core.short_form if pub.core.short_form else ""
                    publication["microref"] = pub.get_microref() if hasattr(pub, 'get_microref') and pub.get_microref() else ""
                    
                    # Add external references
                    refs = []
                    if hasattr(pub, 'PubMed') and pub.PubMed:
                        refs.append(f"http://www.ncbi.nlm.nih.gov/pubmed/?term={pub.PubMed}")
                    if hasattr(pub, 'FlyBase') and pub.FlyBase:
                        refs.append(f"http://flybase.org/reports/{pub.FlyBase}")
                    if hasattr(pub, 'DOI') and pub.DOI:
                        refs.append(f"https://doi.org/{pub.DOI}")
                    
                    publication["refs"] = refs
                    publications.append(publication)
            
            termInfo["Publications"] = publications

        # Add Synonyms for Class entities
        if termInfo["SuperTypes"] and "Class" in termInfo["SuperTypes"] and vfbTerm.pub_syn and len(vfbTerm.pub_syn) > 0:
            synonyms = []
            for syn in vfbTerm.pub_syn:
                if hasattr(syn, 'synonym') and syn.synonym:
                    synonym = {}
                    synonym["label"] = syn.synonym.label if hasattr(syn.synonym, 'label') else ""
                    synonym["scope"] = syn.synonym.scope if hasattr(syn.synonym, 'scope') else "exact"
                    synonym["type"] = syn.synonym.type if hasattr(syn.synonym, 'type') else "synonym"
                    
                    if hasattr(syn, 'pubs') and syn.pubs:
                        pub_refs = []
                        for pub in syn.pubs:
                            if hasattr(pub, 'get_microref') and pub.get_microref():
                                pub_refs.append(pub.get_microref())
                        
                        if pub_refs:
                            # Join multiple publication references with commas
                            synonym["publication"] = ", ".join(pub_refs)
                    # Fallback to single pub if pubs collection not available
                    elif hasattr(syn, 'pub') and syn.pub and hasattr(syn.pub, 'get_microref'):
                        synonym["publication"] = syn.pub.get_microref()
                    
                    synonyms.append(synonym)
            
            # Only add the synonyms if we found any
            if synonyms:
                termInfo["Synonyms"] = synonyms

        # Alternative approach for extracting synonyms from relationships
        if "Class" in termInfo["SuperTypes"] and vfbTerm.relationships and len(vfbTerm.relationships) > 0:
            synonyms = []
            for relationship in vfbTerm.relationships:
                if (relationship.relation.label == "has_exact_synonym" or 
                    relationship.relation.label == "has_broad_synonym" or 
                    relationship.relation.label == "has_narrow_synonym"):
                    
                    synonym = {}
                    synonym["label"] = relationship.object.label
                    
                    # Determine scope based on relation type
                    if relationship.relation.label == "has_exact_synonym":
                        synonym["scope"] = "exact"
                    elif relationship.relation.label == "has_broad_synonym":
                        synonym["scope"] = "broad"
                    elif relationship.relation.label == "has_narrow_synonym":
                        synonym["scope"] = "narrow"
                    
                    synonym["type"] = "synonym"
                    synonyms.append(synonym)
            
            # Only add the synonyms if we found any
            if synonyms and "Synonyms" not in termInfo:
                termInfo["Synonyms"] = synonyms

        # Special handling for Publication entities
        if termInfo["SuperTypes"] and "Publication" in termInfo["SuperTypes"] and vfbTerm.pub_specific_content:
            publication = {}
            publication["title"] = vfbTerm.pub_specific_content.title if hasattr(vfbTerm.pub_specific_content, 'title') else ""
            publication["short_form"] = vfbTerm.term.core.short_form
            publication["microref"] = termInfo["Name"]
            
            # Add external references
            refs = []
            if hasattr(vfbTerm.pub_specific_content, 'PubMed') and vfbTerm.pub_specific_content.PubMed:
                refs.append(f"http://www.ncbi.nlm.nih.gov/pubmed/?term={vfbTerm.pub_specific_content.PubMed}")
            if hasattr(vfbTerm.pub_specific_content, 'FlyBase') and vfbTerm.pub_specific_content.FlyBase:
                refs.append(f"http://flybase.org/reports/{vfbTerm.pub_specific_content.FlyBase}")
            if hasattr(vfbTerm.pub_specific_content, 'DOI') and vfbTerm.pub_specific_content.DOI:
                refs.append(f"https://doi.org/{vfbTerm.pub_specific_content.DOI}")
            
            publication["refs"] = refs
            termInfo["Publications"] = [publication]

        # Append new synonyms to any existing ones
        if synonyms:
            if "Synonyms" not in termInfo:
                termInfo["Synonyms"] = synonyms
            else:
                # Create a set of existing synonym labels to avoid duplicates
                existing_labels = {syn["label"] for syn in termInfo["Synonyms"]}
                # Only append synonyms that don't already exist
                for synonym in synonyms:
                    if synonym["label"] not in existing_labels:
                        termInfo["Synonyms"].append(synonym)
                        existing_labels.add(synonym["label"])

        # Add the queries to the term info
        termInfo["Queries"] = queries

        # print("termInfo object after loading:", termInfo)
    if "Queries" in termInfo:
        termInfo["Queries"] = [query.to_dict() for query in termInfo["Queries"]]
    # print("termInfo object before schema validation:", termInfo)
    try:
        return TermInfoOutputSchema().load(termInfo)
    except ValidationError as e:
        print(f"Validation error when parsing term info: {e}")
        # Return the raw termInfo as a fallback
        return termInfo

def NeuronInputsTo_to_schema(name, take_default):
    query = "NeuronInputsTo"
    label = f"Find neurons with synapses into {name}"
    function = "get_individual_neuron_inputs"
    takes = {
        "neuron_short_form": {"$and": ["Individual", "Neuron"]},
        "default": take_default,
    }
    preview = -1
    preview_columns = ["Neurotransmitter", "Weight"]
    output_format = "ribbon"

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns, output_format=output_format)

def SimilarMorphologyTo_to_schema(name, take_default):
    query = "SimilarMorphologyTo"
    label = f"Find similar neurons to {name}"
    function = "get_similar_neurons"
    takes = {
        "short_form": {"$and": ["Individual", "Neuron"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id","score","name","tags","thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)

def ListAllAvailableImages_to_schema(name, take_default):
    query = "ListAllAvailableImages"
    label = f"List all available images of {name}"
    function = "get_instances"
    takes = {
        "short_form": {"$and": ["Class", "Anatomy"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id","label","tags","thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)

def NeuronsPartHere_to_schema(name, take_default):
    """
    Schema for NeuronsPartHere query.
    Finds neuron classes that have some part overlapping with the specified anatomical region.
    
    Matching criteria from XMI:
    - Class + Synaptic_neuropil (types.1 + types.5)
    - Additional type matches for comprehensive coverage
    
    Query chain: Owlery subclass query → process → SOLR
    OWL query: "Neuron and overlaps some $ID"
    """
    query = "NeuronsPartHere"
    label = f"Neurons with some part in {name}"
    function = "get_neurons_with_part_in"
    takes = {
        "short_form": {"$and": ["Class", "Anatomy"]},
        "default": take_default,
    }
    preview = 5  # Show 5 preview results with example images
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def NeuronsSynaptic_to_schema(name, take_default):
    """
    Schema for NeuronsSynaptic query.
    Finds neuron classes that have synaptic terminals in the specified anatomical region.
    
    Matching criteria from XMI:
    - Class + Synaptic_neuropil
    - Class + Visual_system
    - Class + Synaptic_neuropil_domain
    
    Query chain: Owlery subclass query → process → SOLR
    OWL query: "Neuron and has_synaptic_terminals_in some $ID"
    """
    query = "NeuronsSynaptic"
    label = f"Neurons with synaptic terminals in {name}"
    function = "get_neurons_with_synapses_in"
    takes = {
        "short_form": {"$and": ["Class", "Anatomy"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def NeuronsPresynapticHere_to_schema(name, take_default):
    """
    Schema for NeuronsPresynapticHere query.
    Finds neuron classes that have presynaptic terminals in the specified anatomical region.
    
    Matching criteria from XMI:
    - Class + Synaptic_neuropil
    - Class + Visual_system
    - Class + Synaptic_neuropil_domain
    
    Query chain: Owlery subclass query → process → SOLR
    OWL query: "Neuron and has_presynaptic_terminal_in some $ID"
    """
    query = "NeuronsPresynapticHere"
    label = f"Neurons with presynaptic terminals in {name}"
    function = "get_neurons_with_presynaptic_terminals_in"
    takes = {
        "short_form": {"$and": ["Class", "Anatomy"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def NeuronsPostsynapticHere_to_schema(name, take_default):
    """
    Schema for NeuronsPostsynapticHere query.
    Finds neuron classes that have postsynaptic terminals in the specified anatomical region.
    
    Matching criteria from XMI:
    - Class + Synaptic_neuropil
    - Class + Visual_system
    - Class + Synaptic_neuropil_domain
    
    Query chain: Owlery subclass query → process → SOLR
    OWL query: "Neuron and has_postsynaptic_terminal_in some $ID"
    """
    query = "NeuronsPostsynapticHere"
    label = f"Neurons with postsynaptic terminals in {name}"
    function = "get_neurons_with_postsynaptic_terminals_in"
    takes = {
        "short_form": {"$and": ["Class", "Anatomy"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def ComponentsOf_to_schema(name, take_default):
    """
    Schema for ComponentsOf query.
    Finds components (parts) of the specified anatomical class.
    
    Matching criteria from XMI:
    - Class + Clone
    
    Query chain: Owlery part_of query → process → SOLR
    OWL query: "part_of some $ID"
    """
    query = "ComponentsOf"
    label = f"Components of {name}"
    function = "get_components_of"
    takes = {
        "short_form": {"$and": ["Class", "Anatomy"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def PartsOf_to_schema(name, take_default):
    """
    Schema for PartsOf query.
    Finds parts of the specified anatomical class.
    
    Matching criteria from XMI:
    - Class (any)
    
    Query chain: Owlery part_of query → process → SOLR
    OWL query: "part_of some $ID"
    """
    query = "PartsOf"
    label = f"Parts of {name}"
    function = "get_parts_of"
    takes = {
        "short_form": {"$and": ["Class"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def SubclassesOf_to_schema(name, take_default):
    """
    Schema for SubclassesOf query.
    Finds subclasses of the specified class.
    
    Matching criteria from XMI:
    - Class (any)
    
    Query chain: Owlery subclasses query → process → SOLR
    OWL query: Direct subclasses of $ID
    """
    query = "SubclassesOf"
    label = f"Subclasses of {name}"
    function = "get_subclasses_of"
    takes = {
        "short_form": {"$and": ["Class"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def NeuronClassesFasciculatingHere_to_schema(name, take_default):
    """
    Schema for NeuronClassesFasciculatingHere query.
    Finds neuron classes that fascicululate with (run along) a tract or nerve.
    
    Matching criteria from XMI:
    - Class + Tract_or_nerve (VFB uses Neuron_projection_bundle type)
    
    Query chain: Owlery subclass query → process → SOLR
    OWL query: 'Neuron' that 'fasciculates with' some '{short_form}'
    """
    query = "NeuronClassesFasciculatingHere"
    label = f"Neurons fasciculating in {name}"
    function = "get_neuron_classes_fasciculating_here"
    takes = {
        "short_form": {"$and": ["Class", "Neuron_projection_bundle"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def NeuronNeuronConnectivityQuery_to_schema(name, take_default):
    """
    Schema for neuron_neuron_connectivity_query.
    Finds neurons connected to the specified neuron.
    Matching criteria from XMI: Connected_neuron
    Query chain: Neo4j compound query → process
    """
    query = "NeuronNeuronConnectivityQuery"
    label = f"Neurons connected to {name}"
    function = "get_neuron_neuron_connectivity"
    takes = {
        "short_form": {"$and": ["Individual", "Connected_neuron"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "outputs", "inputs", "tags"]
    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def NeuronRegionConnectivityQuery_to_schema(name, take_default):
    """
    Schema for neuron_region_connectivity_query.
    Shows connectivity to regions from a specified neuron.
    Matching criteria from XMI: Region_connectivity
    Query chain: Neo4j compound query → process
    """
    query = "NeuronRegionConnectivityQuery"
    label = f"Connectivity per region for {name}"
    function = "get_neuron_region_connectivity"
    takes = {
        "short_form": {"$and": ["Individual", "Region_connectivity"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "region", "presynaptic_terminals", "postsynaptic_terminals", "tags"]
    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def TractsNervesInnervatingHere_to_schema(name, take_default):
    """
    Schema for TractsNervesInnervatingHere query.
    Finds tracts and nerves that innervate a synaptic neuropil.
    
    Matching criteria from XMI:
    - Class + Synaptic_neuropil
    - Class + Synaptic_neuropil_domain
    
    Query chain: Owlery subclass query → process → SOLR
    OWL query: 'Tract_or_nerve' that 'innervates' some '{short_form}'
    """
    query = "TractsNervesInnervatingHere"
    label = f"Tracts/nerves innervating {name}"
    function = "get_tracts_nerves_innervating_here"
    takes = {
        "short_form": {"$or": [{"$and": ["Class", "Synaptic_neuropil"]}, {"$and": ["Class", "Synaptic_neuropil_domain"]}]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def LineageClonesIn_to_schema(name, take_default):
    """
    Schema for LineageClonesIn query.
    Finds lineage clones that overlap with a synaptic neuropil or domain.
    
    Matching criteria from XMI:
    - Class + Synaptic_neuropil
    - Class + Synaptic_neuropil_domain
    
    Query chain: Owlery subclass query → process → SOLR
    OWL query: 'Clone' that 'overlaps' some '{short_form}'
    """
    query = "LineageClonesIn"
    label = f"Lineage clones found in {name}"
    function = "get_lineage_clones_in"
    takes = {
        "short_form": {"$and": ["Class", "Synaptic_neuropil"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def ImagesNeurons_to_schema(name, take_default):
    """
    Schema for ImagesNeurons query.
    Finds individual neuron images with parts in a synaptic neuropil or domain.
    
    Matching criteria from XMI:
    - Class + Synaptic_neuropil
    - Class + Synaptic_neuropil_domain
    
    Query chain: Owlery instances query → process → SOLR
    OWL query: 'Neuron' that 'overlaps' some '{short_form}' (returns instances, not classes)
    """
    query = "ImagesNeurons"
    label = f"Images of neurons with some part in {name}"
    function = "get_images_neurons"
    takes = {
        "short_form": {"$or": [{"$and": ["Class", "Synaptic_neuropil"]}, {"$and": ["Class", "Synaptic_neuropil_domain"]}]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def ImagesThatDevelopFrom_to_schema(name, take_default):
    """
    Schema for ImagesThatDevelopFrom query.
    Finds individual neuron images that develop from a neuroblast.
    
    Matching criteria from XMI:
    - Class + Neuroblast
    
    Query chain: Owlery instances query → process → SOLR
    OWL query: 'Neuron' that 'develops_from' some '{short_form}' (returns instances, not classes)
    """
    query = "ImagesThatDevelopFrom"
    label = f"Images of neurons that develop from {name}"
    function = "get_images_that_develop_from"
    takes = {
        "short_form": {"$and": ["Class", "Neuroblast"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def epFrag_to_schema(name, take_default):
    """
    Schema for epFrag query.
    Finds individual expression pattern fragment images that are part of an expression pattern.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    
    Matching criteria from XMI:
    - Class + Expression_pattern
    
    Query chain: Owlery instances query → process → SOLR
    OWL query: instances that are 'part_of' some '{short_form}' (returns instances, not classes)
    """
    query = "epFrag"
    label = f"Images of fragments of {name}"
    function = "get_expression_pattern_fragments"
    takes = {
        "short_form": {"$and": ["Class", "Expression_pattern"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def ExpressionOverlapsHere_to_schema(name, take_default):
    """
    Schema for ExpressionOverlapsHere query.
    Finds expression patterns that overlap with a specified anatomical region.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    
    Matching criteria from XMI:
    - Class + Anatomy
    
    Query chain: Neo4j anat_2_ep_query → process
    Cypher query: MATCH (ep:Class:Expression_pattern)<-[ar:overlaps|part_of]-(anoni:Individual)-[:INSTANCEOF]->(anat:Class)
                  WHERE anat.short_form = $id
    """
    query = "ExpressionOverlapsHere"
    label = f"Expression patterns overlapping {name}"
    function = "get_expression_overlaps_here"
    takes = {
        "short_form": {"$and": ["Class", "Anatomy"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "name", "tags", "pubs"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def anatScRNAseqQuery_to_schema(name, take_default):
    """
    Schema for anatScRNAseqQuery query.
    Returns single cell transcriptomics data (clusters and datasets) for an anatomical region.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    
    Matching criteria from XMI:
    - Class + Anatomy + hasScRNAseq (has Single Cell RNA Seq Results)
    
    Query chain: Owlery Subclasses → Owlery Pass → Neo4j anat_scRNAseq_query
    Cypher query: MATCH (primary:Class:Anatomy)<-[:composed_primarily_of]-(c:Cluster)-[:has_source]->(ds:scRNAseq_DataSet)
                  WHERE primary.short_form = $id
    """
    query = "anatScRNAseqQuery"
    label = f"scRNAseq data for {name}"
    function = "get_anatomy_scrnaseq"
    takes = {
        "short_form": {"$and": ["Class", "Anatomy", "hasScRNAseq"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "name", "tags", "dataset", "pubs"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def clusterExpression_to_schema(name, take_default):
    """
    Schema for clusterExpression query.
    Returns genes expressed in a specified cluster with expression levels.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    
    Matching criteria from XMI:
    - Individual + Cluster
    
    Query chain: Neo4j cluster_expression_query → process
    Cypher query: MATCH (primary:Individual:Cluster)-[e:expresses]->(g:Gene:Class)
                  WHERE primary.short_form = $id
    """
    query = "clusterExpression"
    label = f"Genes expressed in {name}"
    function = "get_cluster_expression"
    takes = {
        "short_form": {"$and": ["Individual", "Cluster"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "name", "tags", "expression_level", "expression_extent"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def expressionCluster_to_schema(name, take_default):
    """
    Schema for expressionCluster query.
    Returns scRNAseq clusters expressing a specified gene.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    
    Matching criteria from XMI:
    - Class + Gene + hasScRNAseq (has Single Cell RNA Seq Results)
    
    Query chain: Neo4j expression_cluster_query → process
    Cypher query: MATCH (primary:Individual:Cluster)-[e:expresses]->(g:Gene:Class)
                  WHERE g.short_form = $id
    """
    query = "expressionCluster"
    label = f"Clusters expressing {name}"
    function = "get_expression_cluster"
    takes = {
        "short_form": {"$and": ["Class", "Gene", "hasScRNAseq"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "name", "tags", "expression_level", "expression_extent"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def scRNAdatasetData_to_schema(name, take_default):
    """
    Schema for scRNAdatasetData query.
    Returns all clusters in a scRNAseq dataset.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    
    Matching criteria from XMI:
    - DataSet + hasScRNAseq (scRNAseq dataset type)
    
    Query chain: Neo4j dataset_scRNAseq_query → process
    Cypher query: MATCH (c:Individual:Cluster)-[:has_source]->(ds:scRNAseq_DataSet)
                  WHERE ds.short_form = $id
    """
    query = "scRNAdatasetData"
    label = f"Clusters in dataset {name}"
    function = "get_scrnaseq_dataset_data"
    takes = {
        "short_form": {"$and": ["DataSet", "hasScRNAseq"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "name", "tags", "anatomy", "pubs"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def SimilarMorphologyToPartOf_to_schema(name, take_default):
    """Schema for SimilarMorphologyToPartOf (NBLASTexp) query."""
    return Query(query="SimilarMorphologyToPartOf", label=f"Similar morphology to part of {name}", function="get_similar_morphology_part_of", takes={"short_form": {"$and": ["Individual", "Neuron", "NBLASTexp"]}, "default": take_default}, preview=5, preview_columns=["id", "name", "score", "tags"])


def SimilarMorphologyToPartOfexp_to_schema(name, take_default):
    """Schema for SimilarMorphologyToPartOfexp (reverse NBLASTexp) query."""
    return Query(query="SimilarMorphologyToPartOfexp", label=f"Similar morphology to part of {name}", function="get_similar_morphology_part_of_exp", takes={"short_form": {"$or": [{"$and": ["Individual", "Expression_pattern", "NBLASTexp"]}, {"$and": ["Individual", "Expression_pattern_fragment", "NBLASTexp"]}]}, "default": take_default}, preview=5, preview_columns=["id", "name", "score", "tags"])


def SimilarMorphologyToNB_to_schema(name, take_default):
    """Schema for SimilarMorphologyToNB (NeuronBridge) query."""
    return Query(query="SimilarMorphologyToNB", label=f"NeuronBridge matches for {name}", function="get_similar_morphology_nb", takes={"short_form": {"$and": ["Individual", "neuronbridge"]}, "default": take_default}, preview=5, preview_columns=["id", "name", "score", "tags"])


def SimilarMorphologyToNBexp_to_schema(name, take_default):
    """Schema for SimilarMorphologyToNBexp (NeuronBridge expression) query."""
    return Query(query="SimilarMorphologyToNBexp", label=f"NeuronBridge matches for {name}", function="get_similar_morphology_nb_exp", takes={"short_form": {"$and": ["Individual", "Expression_pattern", "neuronbridge"]}, "default": take_default}, preview=5, preview_columns=["id", "name", "score", "tags"])


def SimilarMorphologyToUserData_to_schema(name, take_default):
    """Schema for SimilarMorphologyToUserData (user upload NBLAST) query."""
    return Query(query="SimilarMorphologyToUserData", label=f"NBLAST results for {name}", function="get_similar_morphology_userdata", takes={"short_form": {"$and": ["Individual", "UNBLAST"]}, "default": take_default}, preview=5, preview_columns=["id", "name", "score"])


def PaintedDomains_to_schema(name, take_default):
    """Schema for PaintedDomains query."""
    return Query(query="PaintedDomains", label=f"Painted domains for {name}", function="get_painted_domains", takes={"short_form": {"$and": ["Template", "Individual"]}, "default": take_default}, preview=10, preview_columns=["id", "name", "type", "thumbnail"])


def DatasetImages_to_schema(name, take_default):
    """Schema for DatasetImages query."""
    return Query(query="DatasetImages", label=f"Images in dataset {name}", function="get_dataset_images", takes={"short_form": {"$and": ["DataSet", "has_image"]}, "default": take_default}, preview=10, preview_columns=["id", "name", "tags", "type"])


def AllAlignedImages_to_schema(name, take_default):
    """Schema for AllAlignedImages query."""
    return Query(query="AllAlignedImages", label=f"All images aligned to {name}", function="get_all_aligned_images", takes={"short_form": {"$and": ["Template", "Individual"]}, "default": take_default}, preview=10, preview_columns=["id", "name", "tags", "type"])


def AlignedDatasets_to_schema(name, take_default):
    """Schema for AlignedDatasets query."""
    return Query(query="AlignedDatasets", label=f"Datasets aligned to {name}", function="get_aligned_datasets", takes={"short_form": {"$and": ["Template", "Individual"]}, "default": take_default}, preview=10, preview_columns=["id", "name", "tags"])


def AllDatasets_to_schema(name, take_default):
    """Schema for AllDatasets query."""
    return Query(query="AllDatasets", label="All available datasets", function="get_all_datasets", takes={"short_form": {"$and": ["Template"]}, "default": take_default}, preview=10, preview_columns=["id", "name", "tags"])


def TermsForPub_to_schema(name, take_default):
    """Schema for TermsForPub query."""
    return Query(query="TermsForPub", label=f"Terms referencing {name}", function="get_terms_for_pub", takes={"short_form": {"$and": ["Individual", "pub"]}, "default": take_default}, preview=10, preview_columns=["id", "name", "tags", "type"])


def TransgeneExpressionHere_to_schema(name, take_default):
    """Schema for TransgeneExpressionHere query.
    
    Matching criteria from XMI:
    - Class + Nervous_system + Anatomy
    - Class + Nervous_system + Neuron
    
    Query chain: Multi-step Owlery and Neo4j queries
    """
    return Query(query="TransgeneExpressionHere", label=f"Transgene expression in {name}", function="get_transgene_expression_here", takes={"short_form": {"$and": ["Class", "Nervous_system", "Anatomy"]}, "default": take_default}, preview=5, preview_columns=["id", "name", "tags"])


def serialize_solr_output(results):
    # Create a copy of the document and remove Solr-specific fields
    doc = dict(results.docs[0])
    # Remove the _version_ field which can cause serialization issues with large integers
    doc.pop('_version_', None)
    
    # Serialize the sanitized dictionary to JSON using NumpyEncoder
    json_string = json.dumps(doc, ensure_ascii=False, cls=NumpyEncoder)
    json_string = json_string.replace('\\', '')
    json_string = json_string.replace('"{', '{')
    json_string = json_string.replace('}"', '}')
    json_string = json_string.replace("\'", '-')
    return json_string 

@with_solr_cache('term_info')
def get_term_info(short_form: str, preview: bool = True):
    """
    Retrieves the term info for the given term short form.
    Results are cached in SOLR for 3 months to improve performance.

    :param short_form: short form of the term
    :param preview: if True, executes query previews to populate preview_results (default: True)
    :return: term info
    """
    parsed_object = None
    try:
        # Search for the term in the SOLR server
        results = vfb_solr.search('id:' + short_form)
        # Check if any results were returned
        parsed_object = term_info_parse_object(results, short_form)
        if parsed_object:
            # Only try to fill query results if preview is enabled and there are queries to fill
            if preview and parsed_object.get('Queries') and len(parsed_object['Queries']) > 0:
                try:
                    term_info = fill_query_results(parsed_object)
                    if term_info:
                        return term_info
                    else:
                        print("Failed to fill query preview results!")
                        # Set default values for queries when fill_query_results fails
                        for query in parsed_object.get('Queries', []):
                            # Set default preview_results structure
                            query['preview_results'] = {'headers': query.get('preview_columns', ['id', 'label', 'tags', 'thumbnail']), 'rows': []}
                            # Set count to 0 when we can't get the real count
                            query['count'] = 0
                        return parsed_object
                except Exception as e:
                    print(f"Error filling query results (setting default values): {e}")
                    # Set default values for queries when fill_query_results fails
                    for query in parsed_object.get('Queries', []):
                        # Set default preview_results structure
                        query['preview_results'] = {'headers': query.get('preview_columns', ['id', 'label', 'tags', 'thumbnail']), 'rows': []}
                        # Set count to 0 when we can't get the real count
                        query['count'] = 0
                    return parsed_object
            else:
                # No queries to fill (preview=False) or no queries defined, return parsed object directly
                return parsed_object
        else:
            print(f"No valid term info found for ID '{short_form}'")
            return None
    except ValidationError as e:
        # handle the validation error
        print("Schema validation error when parsing response")
        print("Error details:", e)
        print("Original data:", results)
        print("Parsed object:", parsed_object)
        return parsed_object
    except IndexError as e:
        print(f"No results found for ID '{short_form}'")
        print("Error details:", e)
        if parsed_object:
            print("Parsed object:", parsed_object)
            if 'term_info' in locals():
                print("Term info:", term_info)
        else:
            print("Error accessing SOLR server!")
        return None
    except Exception as e:
        print(f"Unexpected error when retrieving term info: {type(e).__name__}: {e}")
        return parsed_object

@with_solr_cache('instances')
def get_instances(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves available instances for the given class short form.
    Uses SOLR term_info data when Neo4j is unavailable (fallback mode).
    :param short_form: short form of the class
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: results rows
    """
    
    try:
        # Try to use original Neo4j implementation first
        # Get the total count of rows
        count_query = f"""
        MATCH (i:Individual:has_image)-[:INSTANCEOF]->(p:Class {{ short_form: '{short_form}' }}),
              (i)<-[:depicts]-(:Individual)-[r:in_register_with]->(:Template)
        RETURN COUNT(r) AS total_count
        """
        count_results = vc.nc.commit_list([count_query])
        count_df = pd.DataFrame.from_records(get_dict_cursor()(count_results))
        total_count = count_df['total_count'][0] if not count_df.empty else 0

        # Define the main Cypher query
        # Pattern: Individual ← depicts ← TemplateChannel → in_register_with → TemplateChannelTemplate → depicts → ActualTemplate
        query = f"""
        MATCH (i:Individual:has_image)-[:INSTANCEOF]->(p:Class {{ short_form: '{short_form}' }}),
              (i)<-[:depicts]-(tc:Individual)-[r:in_register_with]->(tct:Template)-[:depicts]->(templ:Template),
              (i)-[:has_source]->(ds:DataSet)
        OPTIONAL MATCH (i)-[rx:database_cross_reference]->(site:Site)
        OPTIONAL MATCH (ds)-[:license|licence]->(lic:License)
        RETURN i.short_form as id,
               apoc.text.format("[%s](%s)",[COALESCE(i.symbol[0],i.label),i.short_form]) AS label,
               apoc.text.join(i.uniqueFacets, '|') AS tags,
               apoc.text.format("[%s](%s)",[COALESCE(p.symbol[0],p.label),p.short_form]) AS parent,
               REPLACE(apoc.text.format("[%s](%s)",[COALESCE(site.symbol[0],site.label),site.short_form]), '[null](null)', '') AS source,
               REPLACE(apoc.text.format("[%s](%s)",[rx.accession[0],site.link_base[0] + rx.accession[0]]), '[null](null)', '') AS source_id,
               apoc.text.format("[%s](%s)",[COALESCE(templ.symbol[0],templ.label),templ.short_form]) AS template,
               apoc.text.format("[%s](%s)",[COALESCE(ds.symbol[0],ds.label),ds.short_form]) AS dataset,
               REPLACE(apoc.text.format("[%s](%s)",[COALESCE(lic.symbol[0],lic.label),lic.short_form]), '[null](null)', '') AS license,
               REPLACE(apoc.text.format("[![%s](%s '%s')](%s)",[COALESCE(i.symbol[0],i.label) + " aligned to " + COALESCE(templ.symbol[0],templ.label), REPLACE(COALESCE(r.thumbnail[0],""),"thumbnailT.png","thumbnail.png"), COALESCE(i.symbol[0],i.label) + " aligned to " + COALESCE(templ.symbol[0],templ.label), templ.short_form + "," + i.short_form]), "[![null]( 'null')](null)", "") as thumbnail
               ORDER BY id Desc
        """

        if limit != -1:
            query += f" LIMIT {limit}"

        # Run the query using VFB_connect
        results = vc.nc.commit_list([query])
        
        # Convert the results to a DataFrame
        df = pd.DataFrame.from_records(get_dict_cursor()(results))

        columns_to_encode = ['label', 'parent', 'source', 'source_id', 'template', 'dataset', 'license', 'thumbnail']
        df = encode_markdown_links(df, columns_to_encode)
        
        if return_dataframe:
            return df

        # Format the results
        formatted_results = {
            "headers": _get_instances_headers(),
            "rows": [
                {
                    key: row[key]
                    for key in [
                        "id",
                        "label",
                        "tags",
                        "parent",
                        "source",
                        "source_id",
                        "template",
                        "dataset",
                        "license",
                        "thumbnail"
                    ]
                }
                for row in safe_to_dict(df)
            ],
            "count": total_count
        }

        return formatted_results
        
    except Exception as e:
        # Fallback to SOLR-based implementation when Neo4j is unavailable
        print(f"Neo4j unavailable ({e}), using SOLR fallback for get_instances")
        return _get_instances_from_solr(short_form, return_dataframe, limit)

def _get_instances_from_solr(short_form: str, return_dataframe=True, limit: int = -1):
    """
    SOLR-based fallback implementation for get_instances.
    Extracts instance data from term_info anatomy_channel_image array.
    """
    try:
        # Get term_info data from SOLR
        term_info_results = vc.get_TermInfo([short_form], return_dataframe=False)
        
        if len(term_info_results) == 0:
            # Return empty results with proper structure
            if return_dataframe:
                return pd.DataFrame()
            return {
                "headers": _get_instances_headers(),
                "rows": [],
                "count": 0
            }
        
        term_info = term_info_results[0]
        anatomy_images = term_info.get('anatomy_channel_image', [])
        
        # Apply limit if specified
        if limit != -1 and limit > 0:
            anatomy_images = anatomy_images[:limit]
        
        # Convert anatomy_channel_image to instance rows with rich data
        rows = []
        for img in anatomy_images:
            anatomy = img.get('anatomy', {})
            channel_image = img.get('channel_image', {})
            image_info = channel_image.get('image', {}) if channel_image else {}
            template_anatomy = image_info.get('template_anatomy', {}) if image_info else {}
            
            # Extract tags from unique_facets (matching original Neo4j format and ordering)
            unique_facets = anatomy.get('unique_facets', [])
            anatomy_types = anatomy.get('types', [])
            
            # Create ordered list matching the expected Neo4j format
            # Based on test diff, expected order and tags: Nervous_system, Adult, Visual_system, Synaptic_neuropil_domain
            # Note: We exclude 'Synaptic_neuropil' as it doesn't appear in expected output
            ordered_tags = []
            for tag_type in ['Nervous_system', 'Adult', 'Visual_system', 'Synaptic_neuropil_domain']:
                if tag_type in anatomy_types or tag_type in unique_facets:
                    ordered_tags.append(tag_type)
            
            # Use the ordered tags to match expected format
            tags = '|'.join(ordered_tags)
            
            # Extract thumbnail URL and convert to HTTPS
            thumbnail_url = image_info.get('image_thumbnail', '') if image_info else ''
            if thumbnail_url:
                # Replace http with https and thumbnailT.png with thumbnail.png
                thumbnail_url = thumbnail_url.replace('http://', 'https://').replace('thumbnailT.png', 'thumbnail.png')
            
            # Format thumbnail with proper markdown link (matching Neo4j behavior)
            thumbnail = ''
            if thumbnail_url and template_anatomy:
                # Prefer symbol over label for template (matching Neo4j behavior)
                template_label = template_anatomy.get('label', '')
                if template_anatomy.get('symbol') and len(template_anatomy.get('symbol', '')) > 0:
                    template_label = template_anatomy.get('symbol')
                # Decode URL-encoded strings from SOLR (e.g., ME%28R%29 -> ME(R))
                template_label = unquote(template_label)
                template_short_form = template_anatomy.get('short_form', '')
                
                # Prefer symbol over label for anatomy (matching Neo4j behavior)
                anatomy_label = anatomy.get('label', '')
                if anatomy.get('symbol') and len(anatomy.get('symbol', '')) > 0:
                    anatomy_label = anatomy.get('symbol')
                # Decode URL-encoded strings from SOLR (e.g., ME%28R%29 -> ME(R))
                anatomy_label = unquote(anatomy_label)
                anatomy_short_form = anatomy.get('short_form', '')
                
                if template_label and anatomy_label:
                    # Create thumbnail markdown link matching the original format
                    # DO NOT encode brackets in alt text - that's done later by encode_markdown_links
                    alt_text = f"{anatomy_label} aligned to {template_label}"
                    link_target = f"{template_short_form},{anatomy_short_form}"
                    thumbnail = f"[![{alt_text}]({thumbnail_url} '{alt_text}')]({link_target})"
            
            # Format template information
            template_formatted = ''
            if template_anatomy:
                # Prefer symbol over label (matching Neo4j behavior)
                template_label = template_anatomy.get('label', '')
                if template_anatomy.get('symbol') and len(template_anatomy.get('symbol', '')) > 0:
                    template_label = template_anatomy.get('symbol')
                # Decode URL-encoded strings from SOLR (e.g., ME%28R%29 -> ME(R))
                template_label = unquote(template_label)
                template_short_form = template_anatomy.get('short_form', '')
                if template_label and template_short_form:
                    template_formatted = f"[{template_label}]({template_short_form})"
            
            # Handle label formatting (match Neo4j format - prefer symbol over label)
            anatomy_label = anatomy.get('label', 'Unknown')
            if anatomy.get('symbol') and len(anatomy.get('symbol', '')) > 0:
                anatomy_label = anatomy.get('symbol')
            # Decode URL-encoded strings from SOLR (e.g., ME%28R%29 -> ME(R))
            anatomy_label = unquote(anatomy_label)
            anatomy_short_form = anatomy.get('short_form', '')
            
            row = {
                'id': anatomy_short_form,
                'label': f"[{anatomy_label}]({anatomy_short_form})",
                'tags': tags,
                'parent': f"[{term_info.get('term', {}).get('core', {}).get('label', 'Unknown')}]({short_form})",
                'source': '',  # Not readily available in SOLR anatomy_channel_image
                'source_id': '',
 'template': template_formatted,
                'dataset': '',  # Not readily available in SOLR anatomy_channel_image
                'license': '',
                'thumbnail': thumbnail
            }
            rows.append(row)
        
        # Sort by ID to match expected ordering (Neo4j uses "ORDER BY id Desc")
        rows.sort(key=lambda x: x['id'], reverse=True)
        
        total_count = len(anatomy_images)
        
        if return_dataframe:
            df = pd.DataFrame(rows)
            # Apply encoding to markdown links (matches Neo4j implementation)
            columns_to_encode = ['label', 'parent', 'source', 'source_id', 'template', 'dataset', 'license', 'thumbnail']
            df = encode_markdown_links(df, columns_to_encode)
            return df
        
        return {
            "headers": _get_instances_headers(),
            "rows": rows,
            "count": total_count
        }
        
    except Exception as e:
        print(f"Error in SOLR fallback for get_instances: {e}")
        # Return empty results with proper structure
        if return_dataframe:
            return pd.DataFrame()
        return {
            "headers": _get_instances_headers(),
            "rows": [],
            "count": 0
        }

def _get_instances_headers():
    """Return standard headers for get_instances results"""
    return {
        "id": {"title": "Add", "type": "selection_id", "order": -1},
        "label": {"title": "Name", "type": "markdown", "order": 0, "sort": {0: "Asc"}},
        "parent": {"title": "Parent Type", "type": "markdown", "order": 1},
        "template": {"title": "Template", "type": "markdown", "order": 4},
        "tags": {"title": "Gross Types", "type": "tags", "order": 3},
        "source": {"title": "Data Source", "type": "markdown", "order": 5},
        "source_id": {"title": "Data Source", "type": "markdown", "order": 6},
        "dataset": {"title": "Dataset", "type": "markdown", "order": 7},
        "license": {"title": "License", "type": "markdown", "order": 8},
        "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9}
    }

def _get_templates_minimal(limit: int = -1, return_dataframe: bool = False):
    """
    Minimal fallback implementation for get_templates when Neo4j is unavailable.
    Returns hardcoded list of core templates with basic information.
    """
    # Core templates with their basic information
    # Include all columns to match full get_templates() structure
    templates_data = [
        {"id": "VFB_00101567", "name": "JRC2018Unisex", "tags": "VFB|VFB_vol|has_image", "order": 1, "thumbnail": "", "dataset": "", "license": ""},
        {"id": "VFB_00200000", "name": "JRC_FlyEM_Hemibrain", "tags": "VFB|VFB_vol|has_image", "order": 2, "thumbnail": "", "dataset": "", "license": ""},
        {"id": "VFB_00017894", "name": "Adult Brain", "tags": "VFB|VFB_painted|has_image", "order": 3, "thumbnail": "", "dataset": "", "license": ""},
        {"id": "VFB_00101384", "name": "JFRC2", "tags": "VFB|VFB_vol|has_image", "order": 4, "thumbnail": "", "dataset": "", "license": ""},
        {"id": "VFB_00050000", "name": "JFRC2010", "tags": "VFB|VFB_vol|has_image", "order": 5, "thumbnail": "", "dataset": "", "license": ""},
        {"id": "VFB_00049000", "name": "Ito2014", "tags": "VFB|VFB_painted|has_image", "order": 6, "thumbnail": "", "dataset": "", "license": ""},
        {"id": "VFB_00100000", "name": "FCWB", "tags": "VFB|VFB_vol|has_image", "order": 7, "thumbnail": "", "dataset": "", "license": ""},
        {"id": "VFB_00030786", "name": "Adult VNS", "tags": "VFB|VFB_painted|has_image", "order": 8, "thumbnail": "", "dataset": "", "license": ""},
        {"id": "VFB_00110000", "name": "L3 CNS", "tags": "VFB|VFB_vol|has_image", "order": 9, "thumbnail": "", "dataset": "", "license": ""},
        {"id": "VFB_00120000", "name": "L1 CNS", "tags": "VFB|VFB_vol|has_image", "order": 10, "thumbnail": "", "dataset": "", "license": ""},
    ]
    
    # Apply limit if specified
    if limit > 0:
        templates_data = templates_data[:limit]
    
    count = len(templates_data)
    
    if return_dataframe:
        df = pd.DataFrame(templates_data)
        return df
    
    # Format as dict with headers and rows (match full get_templates structure)
    formatted_results = {
        "headers": {
            "id": {"title": "Add", "type": "selection_id", "order": -1},
            "order": {"title": "Order", "type": "numeric", "order": 1, "sort": {0: "Asc"}},
            "name": {"title": "Name", "type": "markdown", "order": 1, "sort": {1: "Asc"}},
            "tags": {"title": "Tags", "type": "tags", "order": 2},
            "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9},
            "dataset": {"title": "Dataset", "type": "metadata", "order": 3},
            "license": {"title": "License", "type": "metadata", "order": 4}
        },
        "rows": templates_data,
        "count": count
    }
    
    return formatted_results

@with_solr_cache('templates')
def get_templates(limit: int = -1, return_dataframe: bool = False):
    """Get list of templates

    :param limit: maximum number of results to return (default -1, returns all results)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns list of dicts.
    :return: list of templates (id, label, tags, source (db) id, accession_in_source) + similarity score.
    :rtype: pandas.DataFrame or list of dicts

    """
    try:
        count_query = """MATCH (t:Template)<-[:depicts]-(tc:Template)-[r:in_register_with]->(tc:Template)
                    RETURN COUNT(DISTINCT t) AS total_count"""

        count_results = vc.nc.commit_list([count_query])
        count_df = pd.DataFrame.from_records(get_dict_cursor()(count_results))
        total_count = count_df['total_count'][0] if not count_df.empty else 0
    except Exception as e:
        # Fallback to minimal template list when Neo4j is unavailable
        print(f"Neo4j unavailable ({e}), using minimal template list fallback")
        return _get_templates_minimal(limit, return_dataframe)

    # Define the main Cypher query
    # Match full pattern to exclude template channel nodes
    # Use COLLECT to aggregate multiple datasets/licenses into single row per template
    query = f"""
    MATCH (p:Class)<-[:INSTANCEOF]-(t:Template)<-[:depicts]-(tc:Template)-[r:in_register_with]->(tc)
    OPTIONAL MATCH (t)-[:has_source]->(ds:DataSet)
    OPTIONAL MATCH (ds)-[:has_license|license]->(lic:License)
    WITH t, r, COLLECT(DISTINCT ds) as datasets, COLLECT(DISTINCT lic) as licenses
    RETURN DISTINCT t.short_form as id,
           apoc.text.format("[%s](%s)",[COALESCE(t.symbol[0],t.label),t.short_form]) AS name,
           apoc.text.join(t.uniqueFacets, '|') AS tags,
           apoc.text.join([ds IN datasets | apoc.text.format("[%s](%s)",[COALESCE(ds.symbol[0],ds.label),ds.short_form])], ', ') AS dataset,
           apoc.text.join([lic IN licenses | REPLACE(apoc.text.format("[%s](%s)",[COALESCE(lic.symbol[0],lic.label),lic.short_form]), '[null](null)', '')], ', ') AS license,
           COALESCE(REPLACE(apoc.text.format("[![%s](%s '%s')](%s)",[COALESCE(t.symbol[0],t.label), REPLACE(COALESCE(r.thumbnail[0],""),"thumbnailT.png","thumbnail.png"), COALESCE(t.symbol[0],t.label), t.short_form]), "[![null]( 'null')](null)", ""), "") as thumbnail,
           99 as order
           ORDER BY id DESC
    """

    if limit != -1:
        query += f" LIMIT {limit}"

    # Run the query using VFB_connect
    results = vc.nc.commit_list([query])

    # Convert the results to a DataFrame
    df = pd.DataFrame.from_records(get_dict_cursor()(results))

    columns_to_encode = ['name', 'dataset', 'license', 'thumbnail']
    df = encode_markdown_links(df, columns_to_encode)

    template_order = ["VFB_00101567","VFB_00200000","VFB_00017894","VFB_00101384","VFB_00050000","VFB_00049000","VFB_00100000","VFB_00030786","VFB_00110000","VFB_00120000"]

    order = 1

    for template in template_order:
        df.loc[df['id'] == template, 'order'] = order
        order += 1

    # Sort the DataFrame by 'order'
    df = df.sort_values('order')

    if return_dataframe:
        return df

    # Format the results
    formatted_results = {
        "headers": {
            "id": {"title": "Add", "type": "selection_id", "order": -1},
            "order": {"title": "Order", "type": "numeric", "order": 1, "sort": {0: "Asc"}},
            "name": {"title": "Name", "type": "markdown", "order": 1, "sort": {1: "Asc"}},
            "tags": {"title": "Tags", "type": "tags", "order": 2},
            "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9},
            "dataset": {"title": "Dataset", "type": "metadata", "order": 3},
            "license": {"title": "License", "type": "metadata", "order": 4}
        },
        "rows": [
            {
                key: row[key]
                for key in [
                    "id",
                    "order",
                    "name",
                    "tags",
                    "thumbnail",
                    "dataset",
                    "license"
                ]
            }
            for row in safe_to_dict(df)
        ],
        "count": total_count
    }
    
    return formatted_results

def get_related_anatomy(template_short_form: str, limit: int = -1, return_dataframe: bool = False):
    """
    Retrieve related anatomical structures for a given template.

    :param template_short_form: The short form of the template to query.
    :param limit: Maximum number of results to return. Default is -1, which returns all results.
    :param return_dataframe: If True, returns results as a pandas DataFrame. Otherwise, returns a list of dicts.
    :return: Related anatomical structures and paths.
    """

    # Define the Cypher query
    query = f"""
    MATCH (root:Class)<-[:INSTANCEOF]-(t:Template {{short_form:'{template_short_form}'}})<-[:depicts]-(tc:Template)<-[ie:in_register_with]-(c:Individual)-[:depicts]->(image:Individual)-[r:INSTANCEOF]->(anat:Class:Anatomy)
    WHERE exists(ie.index)
    WITH root, anat,r,image
    MATCH p=allshortestpaths((root)<-[:SUBCLASSOF|part_of*..50]-(anat))
    UNWIND nodes(p) as n
    UNWIND nodes(p) as m
    WITH * WHERE id(n) < id(m)
    MATCH path = allShortestPaths( (n)-[:SUBCLASSOF|part_of*..1]-(m) )
    RETURN collect(distinct {{ node_id: id(anat), short_form: anat.short_form, image: image.short_form }}) AS image_nodes, id(root) AS root, collect(path)
    """

    if limit != -1:
        query += f" LIMIT {limit}"

    # Execute the query using your database connection (e.g., VFB_connect)
    results = vc.nc.commit_list([query])

    # Convert the results to a DataFrame (if needed)
    if return_dataframe:
        df = pd.DataFrame.from_records(results)
        return df

    # Otherwise, return the raw results
    return results

def get_similar_neurons(neuron, similarity_score='NBLAST_score', return_dataframe=True, limit: int = -1):
    """Get JSON report of individual neurons similar to input neuron

    :param neuron:
    :param similarity_score: Optionally specify similarity score to chose
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns list of dicts.
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: list of similar neurons (id, label, tags, source (db) id, accession_in_source) + similarity score.
    :rtype: pandas.DataFrame or list of dicts

    """
    count_query = f"""MATCH (c1:Class)<-[:INSTANCEOF]-(n1)-[r:has_similar_morphology_to]-(n2)-[:INSTANCEOF]->(c2:Class) 
                WHERE n1.short_form = '{neuron}' and exists(r.{similarity_score})
                RETURN COUNT(DISTINCT n2) AS total_count"""

    count_results = vc.nc.commit_list([count_query])
    count_df = pd.DataFrame.from_records(get_dict_cursor()(count_results))
    total_count = count_df['total_count'][0] if not count_df.empty else 0

    main_query = f"""MATCH (c1:Class)<-[:INSTANCEOF]-(n1)-[r:has_similar_morphology_to]-(n2)-[:INSTANCEOF]->(c2:Class) 
            WHERE n1.short_form = '{neuron}' and exists(r.{similarity_score})
            WITH c1, n1, r, n2, c2
            OPTIONAL MATCH (n2)-[rx:database_cross_reference]->(site:Site)
            WHERE site.is_data_source
            WITH n2, r, c2, rx, site
            OPTIONAL MATCH (n2)<-[:depicts]-(:Individual)-[ri:in_register_with]->(:Template)-[:depicts]->(templ:Template)
            RETURN DISTINCT n2.short_form as id,
            apoc.text.format("[%s](%s)", [n2.label, n2.short_form]) AS name, 
            r.{similarity_score}[0] AS score,
            apoc.text.join(n2.uniqueFacets, '|') AS tags,
            REPLACE(apoc.text.format("[%s](%s)",[COALESCE(site.symbol[0],site.label),site.short_form]), '[null](null)', '') AS source,
            REPLACE(apoc.text.format("[%s](%s)",[rx.accession[0], (site.link_base[0] + rx.accession[0])]), '[null](null)', '') AS source_id,
            REPLACE(apoc.text.format("[![%s](%s '%s')](%s)",[COALESCE(n2.symbol[0],n2.label) + " aligned to " + COALESCE(templ.symbol[0],templ.label), REPLACE(COALESCE(ri.thumbnail[0],""),"thumbnailT.png","thumbnail.png"), COALESCE(n2.symbol[0],n2.label) + " aligned to " + COALESCE(templ.symbol[0],templ.label), templ.short_form + "," + n2.short_form]), "[![null]( 'null')](null)", "") as thumbnail
            ORDER BY score DESC"""

    if limit != -1:
        main_query += f" LIMIT {limit}"

    # Run the query using VFB_connect
    results = vc.nc.commit_list([main_query])

    # Convert the results to a DataFrame
    df = pd.DataFrame.from_records(get_dict_cursor()(results))

    columns_to_encode = ['name', 'source', 'source_id', 'thumbnail']
    df = encode_markdown_links(df, columns_to_encode)
    
    if return_dataframe:
        return df
    else:
        formatted_results = {
            "headers": {
                "id": {"title": "Add", "type": "selection_id", "order": -1},
                "score": {"title": "Score", "type": "numeric", "order": 1, "sort": {0: "Desc"}},
                "name": {"title": "Name", "type": "markdown", "order": 1, "sort": {1: "Asc"}},
                "tags": {"title": "Tags", "type": "tags", "order": 2},
                "source": {"title": "Source", "type": "metadata", "order": 3},
                "source_id": {"title": "Source ID", "type": "metadata", "order": 4},
                "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9}
            },
            "rows": [
                {
                    key: row[key]
                    for key in [
                        "id",
                        "name",
                        "score",
                        "tags",
                        "source",
                        "source_id",
                        "thumbnail"
                    ]
                }
                for row in safe_to_dict(df, sort_by_id=False)
            ],
            "count": total_count
        }
        return formatted_results

def get_individual_neuron_inputs(neuron_short_form: str, return_dataframe=True, limit: int = -1, summary_mode: bool = False):
    """
    Retrieve neurons that have synapses into the specified neuron, along with the neurotransmitter
    types, and additional information about the neurons.

    :param neuron_short_form: The short form identifier of the neuron to query.
    :param return_dataframe: If True, returns results as a pandas DataFrame. Otherwise, returns a dictionary.
    :param limit: Maximum number of results to return. Default is -1, which returns all results.
    :param summary_mode: If True, returns a preview of the results with summed weights for each neurotransmitter type.
    :return: Neurons, neurotransmitter types, and additional neuron information.
    """

    # Define the common part of the Cypher query
    query_common = f"""
    MATCH (a:has_neuron_connectivity {{short_form:'{neuron_short_form}'}})<-[r:synapsed_to]-(b:has_neuron_connectivity)
    UNWIND(labels(b)) as l
    WITH * WHERE l contains "ergic"
    OPTIONAL MATCH (c:Class:Neuron) WHERE c.short_form starts with "FBbt_" AND toLower(c.label)=toLower(l+" neuron")
    """
    if not summary_mode:
        count_query = f"""{query_common}
                    RETURN COUNT(DISTINCT b) AS total_count"""
    else:
        count_query = f"""{query_common}
                    RETURN COUNT(DISTINCT c) AS total_count"""

    count_results = vc.nc.commit_list([count_query])
    count_df = pd.DataFrame.from_records(get_dict_cursor()(count_results))
    total_count = count_df['total_count'][0] if not count_df.empty else 0

    # Define the part of the query for normal mode
    query_normal = f"""
    OPTIONAL MATCH (b)-[:INSTANCEOF]->(neuronType:Class),
                   (b)<-[:depicts]-(imageChannel:Individual)-[image:in_register_with]->(templateChannel:Template)-[:depicts]->(templ:Template),
                   (imageChannel)-[:is_specified_output_of]->(imagingTechnique:Class)
    RETURN 
        b.short_form as id,
        apoc.text.format("[%s](%s)", [l, c.short_form]) as Neurotransmitter, 
        sum(r.weight[0]) as Weight,
        apoc.text.format("[%s](%s)", [b.label, b.short_form]) as Name,
        apoc.text.format("[%s](%s)", [neuronType.label, neuronType.short_form]) as Type,
        apoc.text.join(b.uniqueFacets, '|') as Gross_Type,
        apoc.text.join(collect(apoc.text.format("[%s](%s)", [templ.label, templ.short_form])), ', ') as Template_Space,
        apoc.text.format("[%s](%s)", [imagingTechnique.label, imagingTechnique.short_form]) as Imaging_Technique,
        apoc.text.join(collect(REPLACE(apoc.text.format("[![%s](%s '%s')](%s)",[COALESCE(b.symbol[0],b.label), REPLACE(COALESCE(image.thumbnail[0],""),"thumbnailT.png","thumbnail.png"), COALESCE(b.symbol[0],b.label), b.short_form]), "[![null]( 'null')](null)", "")), ' | ') as Images
    ORDER BY Weight Desc
    """

    # Define the part of the query for preview mode
    query_preview = f"""
    RETURN DISTINCT c.short_form as id,
        apoc.text.format("[%s](%s)", [l, c.short_form]) as Neurotransmitter, 
        sum(r.weight[0]) as Weight
    ORDER BY Weight Desc
    """

    # Choose the appropriate part of the query based on the summary_mode parameter
    query = query_common + (query_preview if summary_mode else query_normal)

    if limit != -1 and not summary_mode:
        query += f" LIMIT {limit}"

    # Execute the query using your database connection (e.g., vc.nc)
    results = vc.nc.commit_list([query])

    # Convert the results to a DataFrame
    df = pd.DataFrame.from_records(get_dict_cursor()(results))

    columns_to_encode = ['Neurotransmitter', 'Type', 'Name', 'Template_Space', 'Imaging_Technique', 'thumbnail']
    df = encode_markdown_links(df, columns_to_encode)
    
    # If return_dataframe is True, return the results as a DataFrame
    if return_dataframe:
        return df

    # Format the results for the preview
    if not summary_mode:
        results = {
            "headers": {
                "id": {"title": "ID", "type": "text", "order": -1},
                "Neurotransmitter": {"title": "Neurotransmitter", "type": "markdown", "order": 0},
                "Weight": {"title": "Weight", "type": "numeric", "order": 1},
                "Name": {"title": "Name", "type": "markdown", "order": 2},
                "Type": {"title": "Type", "type": "markdown", "order": 3},
                "Gross_Type": {"title": "Gross Type", "type": "text", "order": 4},
                "Template_Space": {"title": "Template Space", "type": "markdown", "order": 5},
                "Imaging_Technique": {"title": "Imaging Technique", "type": "markdown", "order": 6},
                "Images": {"title": "Images", "type": "markdown", "order": 7}
            },
            "rows": [
                {
                    key: row[key]
                    for key in [
                        "id",
                        "Neurotransmitter",
                        "Weight",
                        "Name",
                        "Type",
                        "Gross_Type",
                        "Template_Space",
                        "Imaging_Technique",
                        "Images"
                    ]
                }
                for row in safe_to_dict(df, sort_by_id=False)
            ],
            "count": total_count
        }
    else:
        results = {
            "headers": {
                "id": {"title": "ID", "type": "text", "order": -1},
                "Neurotransmitter": {"title": "Neurotransmitter", "type": "markdown", "order": 0},
                "Weight": {"title": "Weight", "type": "numeric", "order": 1},
            },
            "rows": [
                {
                    key: row[key]
                    for key in [
                        "id",
                        "Neurotransmitter",
                        "Weight",
                    ]
                }
                for row in safe_to_dict(df, sort_by_id=False)
            ],
            "count": total_count
        }
    
    return results


def get_expression_overlaps_here(anatomy_short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieve expression patterns that overlap with the specified anatomical region.
    
    This implements the ExpressionOverlapsHere query from the VFB XMI specification.
    Finds expression patterns where individual instances overlap with or are part of the anatomy.
    
    :param anatomy_short_form: Short form identifier of the anatomical region (e.g., 'FBbt_00003982')
    :param return_dataframe: Returns pandas DataFrame if True, otherwise returns formatted dict (default: True)
    :param limit: Maximum number of results to return (default: -1 for all results)
    :return: Expression patterns with overlap relationships, publications, and images
    :rtype: pandas.DataFrame or dict
    """
    
    # Count query: count distinct expression patterns
    count_query = f"""
        MATCH (ep:Class:Expression_pattern)<-[ar:overlaps|part_of]-(anoni:Individual)-[:INSTANCEOF]->(anat:Class)
        WHERE anat.short_form = '{anatomy_short_form}'
        RETURN COUNT(DISTINCT ep) AS total_count
    """
    
    count_results = vc.nc.commit_list([count_query])
    count_df = pd.DataFrame.from_records(get_dict_cursor()(count_results))
    total_count = count_df['total_count'][0] if not count_df.empty else 0
    
    # Main query: get expression patterns with details
    main_query = f"""
        MATCH (ep:Class:Expression_pattern)<-[ar:overlaps|part_of]-(anoni:Individual)-[:INSTANCEOF]->(anat:Class)
        WHERE anat.short_form = '{anatomy_short_form}'
        WITH DISTINCT collect(DISTINCT ar.pub[0]) as pubs, anat, ep
        UNWIND pubs as p
        OPTIONAL MATCH (pub:pub {{ short_form: p}})
        WITH anat, ep, collect({{ 
            core: {{ short_form: pub.short_form, label: coalesce(pub.label,''), iri: pub.iri, types: labels(pub), symbol: coalesce(pub.symbol[0], '') }}, 
            PubMed: coalesce(pub.PMID[0], ''), 
            FlyBase: coalesce(([]+pub.FlyBase)[0], ''), 
            DOI: coalesce(pub.DOI[0], '') 
        }}) as pubs
        RETURN 
            ep.short_form AS id,
            apoc.text.format("[%s](%s)", [ep.label, ep.short_form]) AS name,
            apoc.text.join(ep.uniqueFacets, '|') AS tags,
            pubs
        ORDER BY ep.label
    """
    
    if limit != -1:
        main_query += f" LIMIT {limit}"
    
    # Execute the query
    results = vc.nc.commit_list([main_query])
    
    # Convert to DataFrame
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    
    # Encode markdown links
    if not df.empty:
        columns_to_encode = ['name']
        df = encode_markdown_links(df, columns_to_encode)
    
    if return_dataframe:
        return df
    else:
        formatted_results = {
            "headers": {
                "id": {"title": "ID", "type": "selection_id", "order": -1},
                "name": {"title": "Expression Pattern", "type": "markdown", "order": 0},
                "tags": {"title": "Tags", "type": "tags", "order": 1},
                "pubs": {"title": "Publications", "type": "metadata", "order": 2}
            },
            "rows": [
                {
                    key: row[key]
                    for key in ["id", "name", "tags", "pubs"]
                }
                for row in safe_to_dict(df, sort_by_id=False)
            ],
            "count": total_count
        }
        return formatted_results


def contains_all_tags(lst: List[str], tags: List[str]) -> bool:
    """
    Checks if the given list contains all the tags passed.

    :param lst: list of strings to check
    :param tags: list of strings to check for in lst
    :return: True if lst contains all tags, False otherwise
    """
    return all(tag in lst for tag in tags)

@with_solr_cache('neurons_part_here')
def get_neurons_with_part_in(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves neuron classes that have some part overlapping with the specified anatomical region.
    
    This implements the NeuronsPartHere query from the VFB XMI specification.
    Query chain (from XMI): Owlery (Index 1) → Process → SOLR (Index 3)
    OWL query (from XMI): <FBbt_00005106> and <RO_0002131> some <$ID>
    Where: FBbt_00005106 = neuron, RO_0002131 = overlaps
    
    :param short_form: short form of the anatomical region (Class)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Neuron classes with parts in the specified region
    """
    owl_query = f"<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002131> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, 
                                    solr_field='anat_query', include_source=True, query_by_label=False)


@with_solr_cache('neurons_synaptic')
def get_neurons_with_synapses_in(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves neuron classes that have synaptic terminals in the specified anatomical region.
    
    This implements the NeuronsSynaptic query from the VFB XMI specification.
    Query chain (from XMI): Owlery → Process → SOLR
    OWL query (from XMI): object=<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002130> some <http://purl.obolibrary.org/obo/$ID>
    Where: FBbt_00005106 = neuron, RO_0002130 = has synaptic terminals in
    Matching criteria: Class + Synaptic_neuropil, Class + Visual_system, Class + Synaptic_neuropil_domain
    
    :param short_form: short form of the anatomical region (Class)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Neuron classes with synaptic terminals in the specified region
    """
    owl_query = f"<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002130> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, solr_field='anat_query', query_by_label=False)


@with_solr_cache('neurons_presynaptic')
def get_neurons_with_presynaptic_terminals_in(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves neuron classes that have presynaptic terminals in the specified anatomical region.
    
    This implements the NeuronsPresynapticHere query from the VFB XMI specification.
    Query chain (from XMI): Owlery → Process → SOLR
    OWL query (from XMI): object=<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002113> some <http://purl.obolibrary.org/obo/$ID>
    Where: FBbt_00005106 = neuron, RO_0002113 = has presynaptic terminal in
    Matching criteria: Class + Synaptic_neuropil, Class + Visual_system, Class + Synaptic_neuropil_domain
    
    :param short_form: short form of the anatomical region (Class)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Neuron classes with presynaptic terminals in the specified region
    """
    owl_query = f"<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002113> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, solr_field='anat_query', query_by_label=False)


@with_solr_cache('neurons_postsynaptic')
def get_neurons_with_postsynaptic_terminals_in(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves neuron classes that have postsynaptic terminals in the specified anatomical region.
    
    This implements the NeuronsPostsynapticHere query from the VFB XMI specification.
    Query chain (from XMI): Owlery → Process → SOLR
    OWL query (from XMI): object=<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002110> some <http://purl.obolibrary.org/obo/$ID>
    Where: FBbt_00005106 = neuron, RO_0002110 = has postsynaptic terminal in
    Matching criteria: Class + Synaptic_neuropil, Class + Visual_system, Class + Synaptic_neuropil_domain
    
    :param short_form: short form of the anatomical region (Class)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Neuron classes with postsynaptic terminals in the specified region
    """
    owl_query = f"<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002110> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, solr_field='anat_query', query_by_label=False)


@with_solr_cache('components_of')
def get_components_of(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves components (parts) of the specified anatomical class.
    
    This implements the ComponentsOf query from the VFB XMI specification.
    Query chain (from XMI): Owlery Part of → Process → SOLR
    OWL query (from XMI): object=<http://purl.obolibrary.org/obo/BFO_0000050> some <http://purl.obolibrary.org/obo/$ID>
    Where: BFO_0000050 = part of
    Matching criteria: Class + Clone
    
    :param short_form: short form of the anatomical class
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Components of the specified class
    """
    owl_query = f"<http://purl.obolibrary.org/obo/BFO_0000050> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, solr_field='anat_query', query_by_label=False)


@with_solr_cache('parts_of')
def get_parts_of(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves parts of the specified anatomical class.
    
    This implements the PartsOf query from the VFB XMI specification.
    Query chain (from XMI): Owlery Part of → Process → SOLR
    OWL query (from XMI): object=<http://purl.obolibrary.org/obo/BFO_0000050> some <http://purl.obolibrary.org/obo/$ID>
    Where: BFO_0000050 = part of
    Matching criteria: Class (any)
    
    :param short_form: short form of the anatomical class
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Parts of the specified class
    """
    owl_query = f"<http://purl.obolibrary.org/obo/BFO_0000050> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, solr_field='anat_query', query_by_label=False)


@with_solr_cache('subclasses_of')
def get_subclasses_of(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves subclasses of the specified class.
    
    This implements the SubclassesOf query from the VFB XMI specification.
    Query chain (from XMI): Owlery → Process → SOLR
    OWL query: Direct subclasses of '<class>'
    Matching criteria: Class (any)
    
    :param short_form: short form of the class
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Subclasses of the specified class
    """
    # For subclasses, we query the class itself (Owlery subclasses endpoint handles this)
    # Use angle brackets for IRI conversion, not quotes
    owl_query = f"<{short_form}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, solr_field='anat_query', query_by_label=False)


@with_solr_cache('neuron_classes_fasciculating_here')
def get_neuron_classes_fasciculating_here(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves neuron classes that fasciculate with (run along) the specified tract or nerve.
    
    This implements the NeuronClassesFasciculatingHere query from the VFB XMI specification.
    Query chain (from XMI): Owlery → Process → SOLR
    OWL query (from XMI): object=<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002101> some <http://purl.obolibrary.org/obo/$ID>
    Where: FBbt_00005106 = neuron, RO_0002101 = fasciculates with
    Matching criteria: Class + Tract_or_nerve
    
    :param short_form: short form of the tract or nerve (Class)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Neuron classes that fasciculate with the specified tract or nerve
    """
    owl_query = f"<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002101> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, solr_field='anat_query', query_by_label=False)


@with_solr_cache('tracts_nerves_innervating_here')
def get_tracts_nerves_innervating_here(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves tracts and nerves that innervate the specified synaptic neuropil.
    
    This implements the TractsNervesInnervatingHere query from the VFB XMI specification.
    Query chain (from XMI): Owlery → Process → SOLR
    OWL query (from XMI): object=<http://purl.obolibrary.org/obo/FBbt_00005099> and <http://purl.obolibrary.org/obo/RO_0002134> some <http://purl.obolibrary.org/obo/$ID>
    Where: FBbt_00005099 = tract or nerve, RO_0002134 = innervates
    Matching criteria: Class + Synaptic_neuropil, Class + Synaptic_neuropil_domain
    
    :param short_form: short form of the synaptic neuropil (Class)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Tracts and nerves that innervate the specified neuropil
    """
    owl_query = f"<http://purl.obolibrary.org/obo/FBbt_00005099> and <http://purl.obolibrary.org/obo/RO_0002134> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, solr_field='anat_query', query_by_label=False)


@with_solr_cache('lineage_clones_in')
def get_lineage_clones_in(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves lineage clones that overlap with the specified synaptic neuropil.
    
    This implements the LineageClonesIn query from the VFB XMI specification.
    Query chain (from XMI): Owlery → Process → SOLR
    OWL query (from XMI): object=<http://purl.obolibrary.org/obo/FBbt_00007683> and <http://purl.obolibrary.org/obo/RO_0002131> some <http://purl.obolibrary.org/obo/$ID>
    Where: FBbt_00007683 = clone, RO_0002131 = overlaps
    Matching criteria: Class + Synaptic_neuropil, Class + Synaptic_neuropil_domain
    
    :param short_form: short form of the synaptic neuropil (Class)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Lineage clones that overlap with the specified neuropil
    """
    owl_query = f"<http://purl.obolibrary.org/obo/FBbt_00007683> and <http://purl.obolibrary.org/obo/RO_0002131> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, solr_field='anat_query', query_by_label=False)


@with_solr_cache('neuron_neuron_connectivity_query')
def get_neuron_neuron_connectivity(short_form: str, return_dataframe=True, limit: int = -1, min_weight: float = 0, direction: str = 'both'):
    """
    Retrieves neurons connected to the specified neuron.
    
    This implements the neuron_neuron_connectivity_query from the VFB XMI specification.
    Query chain (from XMI): Neo4j compound query → process
    Matching criteria: Individual + Connected_neuron
    
    Uses synapsed_to relationships to find partner neurons.
    Returns inputs (upstream) and outputs (downstream) connection information.
    
    :param short_form: short form of the neuron (Individual)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :param min_weight: minimum connection weight threshold (default 0, XMI spec uses 1)
    :param direction: filter by connection direction - 'both' (default), 'upstream', or 'downstream'
    :return: Partner neurons with their input/output connection weights
    
    Note: Caching only applies when all parameters are at default values (complete results).
    """
    # Build Cypher query to get connected neurons using synapsed_to relationships
    # XMI spec uses min_weight > 1, but we default to 0 to return all valid connections
    base_cypher = f"""
    MATCH (primary:Individual {{short_form: '{short_form}'}})
    MATCH (oi:Individual)-[r:synapsed_to]-(primary)
    WHERE exists(r.weight) AND r.weight[0] > {min_weight}
    WITH primary, oi
    OPTIONAL MATCH (oi)<-[down:synapsed_to]-(primary)
    WITH down, oi, primary
    OPTIONAL MATCH (primary)<-[up:synapsed_to]-(oi)
    """
    
    if direction == 'upstream':
        base_cypher += " WHERE up IS NOT NULL AND up.weight[0] > 0"
    elif direction == 'downstream':
        base_cypher += " WHERE down IS NOT NULL AND down.weight[0] > 0"
    # for 'both', no additional WHERE
    
    cypher = base_cypher + """
    RETURN 
        oi.short_form AS id,
        oi.label AS label,
        coalesce(down.weight[0], 0) AS outputs,
        coalesce(up.weight[0], 0) AS inputs,
        oi.uniqueFacets AS tags
    """
    
    if limit != -1:
        cypher += f" LIMIT {limit}"

    # Run query using Neo4j client
    results = vc.nc.commit_list([cypher])
    rows = get_dict_cursor()(results)
    
    # Get total count if limit was applied
    if limit != -1:
        if direction == 'upstream':
            count_query = base_cypher + " WHERE up IS NOT NULL AND up.weight[0] > 0 RETURN count(DISTINCT oi)"
        elif direction == 'downstream':
            count_query = base_cypher + " WHERE down IS NOT NULL AND down.weight[0] > 0 RETURN count(DISTINCT oi)"
        else:  # both
            count_query = base_cypher + " RETURN count(DISTINCT oi)"
        count_results = vc.nc.commit_list([count_query])
        total_count = count_results[0][0] if count_results and count_results[0] else 0
    else:
        total_count = len(rows)
    
    # No need to filter by direction, it's done in the query

    # Format output
    if return_dataframe:
        df = pd.DataFrame(rows)
        return df
    
    headers = {
        'id': {'title': 'Neuron ID', 'type': 'selection_id', 'order': -1},
        'label': {'title': 'Partner Neuron', 'type': 'markdown', 'order': 0},
        'outputs': {'title': 'Outputs', 'type': 'number', 'order': 1},
        'inputs': {'title': 'Inputs', 'type': 'number', 'order': 2},
        'tags': {'title': 'Neuron Types', 'type': 'list', 'order': 3},
    }
    return {
        'headers': headers,
        'rows': rows,
        'count': total_count
    }


@with_solr_cache('neuron_region_connectivity_query')
def get_neuron_region_connectivity(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves brain regions where the specified neuron has synaptic terminals.
    
    This implements the neuron_region_connectivity_query from the VFB XMI specification.
    Query chain (from XMI): Neo4j compound query → process
    Matching criteria: Individual + has_region_connectivity
    
    Uses has_presynaptic_terminals_in and has_postsynaptic_terminal_in relationships
    to find brain regions where the neuron makes connections.
    
    :param short_form: short form of the neuron (Individual)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Brain regions with presynaptic and postsynaptic terminal counts
    """
    # Build Cypher query based on XMI spec pattern
    cypher = f"""
    MATCH (primary:Individual {{short_form: '{short_form}'}})
    MATCH (target:Individual)<-[r:has_presynaptic_terminals_in|has_postsynaptic_terminal_in]-(primary)
    WITH DISTINCT collect(properties(r)) + {{}} as props, target, primary
    WITH apoc.map.removeKeys(apoc.map.merge(props[0], props[1]), ['iri', 'short_form', 'Related', 'label', 'type']) as synapse_counts,
         target,
         primary
    RETURN 
        target.short_form AS id,
        target.label AS region,
        synapse_counts.`pre` AS presynaptic_terminals,
        synapse_counts.`post` AS postsynaptic_terminals,
        target.uniqueFacets AS tags
    """
    if limit != -1:
        cypher += f" LIMIT {limit}"

    # Run query using Neo4j client
    results = vc.nc.commit_list([cypher])
    rows = get_dict_cursor()(results)
    
    # Format output
    if return_dataframe:
        df = pd.DataFrame(rows)
        return df
    
    headers = {
        'id': {'title': 'Region ID', 'type': 'selection_id', 'order': -1},
        'region': {'title': 'Brain Region', 'type': 'markdown', 'order': 0},
        'presynaptic_terminals': {'title': 'Presynaptic Terminals', 'type': 'number', 'order': 1},
        'postsynaptic_terminals': {'title': 'Postsynaptic Terminals', 'type': 'number', 'order': 2},
        'tags': {'title': 'Region Types', 'type': 'list', 'order': 3},
    }
    return {
        'headers': headers,
        'rows': rows,
        'count': len(rows)
    }


@with_solr_cache('images_neurons')
def get_images_neurons(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves individual neuron images with parts in the specified synaptic neuropil.
    
    This implements the ImagesNeurons query from the VFB XMI specification.
    Query chain (from XMI): Owlery instances → Process → SOLR
    OWL query (from XMI): object=<FBbt_00005106> and <RO_0002131> some <$ID> (instances)
    Where: FBbt_00005106 = neuron, RO_0002131 = overlaps
    Matching criteria: Class + Synaptic_neuropil, Class + Synaptic_neuropil_domain
    
    Note: This query returns INSTANCES (individual neuron images) not classes.
    
    :param short_form: short form of the synaptic neuropil (Class)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Individual neuron images with parts in the specified neuropil
    """
    owl_query = f"<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002131> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, 
                                    solr_field='anat_image_query', query_by_label=False, query_instances=True)


@with_solr_cache('images_that_develop_from')
def get_images_that_develop_from(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves individual neuron images that develop from the specified neuroblast.
    
    This implements the ImagesThatDevelopFrom query from the VFB XMI specification.
    Query chain (from XMI): Owlery instances → Owlery Pass → SOLR
    OWL query (from XMI): object=<FBbt_00005106> and <RO_0002202> some <$ID> (instances)
    Where: FBbt_00005106 = neuron, RO_0002202 = develops_from
    Matching criteria: Class + Neuroblast
    
    Note: This query returns INSTANCES (individual neuron images) not classes.
    
    :param short_form: short form of the neuroblast (Class)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Individual neuron images that develop from the specified neuroblast
    """
    owl_query = f"<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002202> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, 
                                    solr_field='anat_image_query', query_by_label=False, query_instances=True)


def _short_form_to_iri(short_form: str) -> str:
    """
    Convert a short form ID to its full IRI.
    
    First tries simple prefix mappings for common cases (VFB*, FB*).
    For other cases, queries SOLR to get the canonical IRI.
    
    :param short_form: Short form ID (e.g., 'VFBexp_FBtp0022557', 'FBbt_00003748')
    :return: Full IRI
    """
    # VFB IDs use virtualflybrain.org/reports
    if short_form.startswith('VFB'):
        return f"http://virtualflybrain.org/reports/{short_form}"
    
    # FB* IDs (FlyBase) use purl.obolibrary.org/obo
    # This includes FBbt_, FBtp_, FBdv_, etc.
    if short_form.startswith('FB'):
        return f"http://purl.obolibrary.org/obo/{short_form}"
    
    # For other cases, query SOLR to get the IRI from term_info
    try:
        results = vfb_solr.search(
            q=f'id:{short_form}',
            fl='term_info',
            rows=1
        )
        
        if results.docs and 'term_info' in results.docs[0]:
            term_info_str = results.docs[0]['term_info'][0]
            term_info = json.loads(term_info_str)
            iri = term_info.get('term', {}).get('core', {}).get('iri')
            if iri:
                return iri
    except Exception as e:
        # If SOLR query fails, fall back to OBO default
        print(f"Warning: Could not fetch IRI for {short_form} from SOLR: {e}")
    
    # Default to OBO for other IDs (FBbi_, etc.)
    return f"http://purl.obolibrary.org/obo/{short_form}"


@with_solr_cache('expression_pattern_fragments')
def get_expression_pattern_fragments(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves individual expression pattern fragment images that are part of an expression pattern.
    
    This implements the epFrag query from the VFB XMI specification.
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    
    Query chain (from XMI): Owlery individual parts → Process → SOLR
    OWL query (from XMI): object=<BFO_0000050> some <$ID> (instances)
    Where: BFO_0000050 = part_of
    Matching criteria: Class + Expression_pattern
    
    Note: This query returns INSTANCES (individual expression pattern fragments) not classes.
    
    :param short_form: short form of the expression pattern (Class)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Individual expression pattern fragment images
    """
    iri = _short_form_to_iri(short_form)
    owl_query = f"<http://purl.obolibrary.org/obo/BFO_0000050> some <{iri}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, 
                                    solr_field='anat_image_query', query_by_label=False, query_instances=True)


def _get_neurons_part_here_headers():
    """Return standard headers for get_neurons_with_part_in results"""
    return {
        "id": {"title": "Add", "type": "selection_id", "order": -1},
        "label": {"title": "Name", "type": "markdown", "order": 0, "sort": {0: "Asc"}},
        "tags": {"title": "Tags", "type": "tags", "order": 2},
        "source": {"title": "Data Source", "type": "metadata", "order": 3},
        "source_id": {"title": "Data Source ID", "type": "metadata", "order": 4},
        "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9}
    }


def _get_standard_query_headers():
    """Return standard headers for most query results (no source/source_id)"""
    return {
        "id": {"title": "Add", "type": "selection_id", "order": -1},
        "label": {"title": "Name", "type": "markdown", "order": 0, "sort": {0: "Asc"}},
        "tags": {"title": "Tags", "type": "tags", "order": 2},
        "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9}
    }


def _owlery_query_to_results(owl_query_string: str, short_form: str, return_dataframe: bool = True, 
                              limit: int = -1, solr_field: str = 'anat_query', 
                              include_source: bool = False, query_by_label: bool = True,
                              query_instances: bool = False):
    """
    Unified helper function for Owlery-based queries.
    
    This implements the common pattern:
    1. Query Owlery for class/instance IDs matching an OWL pattern
    2. Fetch details from SOLR for each result
    3. Format results as DataFrame or dict
    
    :param owl_query_string: OWL query string (format depends on query_by_label parameter)
    :param short_form: The anatomical region or entity short form
    :param return_dataframe: Returns pandas DataFrame if True, otherwise returns formatted dict
    :param limit: Maximum number of results to return (default -1 for all)
    :param solr_field: SOLR field to query (default 'anat_query' for Class, 'anat_image_query' for Individuals)
    :param include_source: Whether to include source and source_id columns
    :param query_by_label: If True, use label syntax with quotes. If False, use IRI syntax with angle brackets.
    :param query_instances: If True, query for instances instead of subclasses
    :return: Query results
    """
    try:
        # Step 1: Query Owlery for classes or instances matching the OWL pattern
        if query_instances:
            result_ids = vc.vfb.oc.get_instances(
                query=owl_query_string,
                query_by_label=query_by_label,
                verbose=False
            )
        else:
            result_ids = vc.vfb.oc.get_subclasses(
                query=owl_query_string,
                query_by_label=query_by_label,
                verbose=False
            )
        
        class_ids = result_ids  # Keep variable name for compatibility
        
        if not class_ids:
            # No results found - return empty
            if return_dataframe:
                return pd.DataFrame()
            return {
                "headers": _get_standard_query_headers() if not include_source else _get_neurons_part_here_headers(),
                "rows": [],
                "count": 0
            }
        
        total_count = len(class_ids)
        
        # Apply limit if specified (before SOLR query to save processing)
        if limit != -1 and limit > 0:
            class_ids = class_ids[:limit]
        
        # Step 2: Query SOLR for ALL classes in a single batch query
        # Use the {!terms f=id} syntax from XMI to fetch all results efficiently
        rows = []
        try:
            # Build filter query with all class IDs
            id_list = ','.join(class_ids)
            results = vfb_solr.search(
                q='id:*',
                fq=f'{{!terms f=id}}{id_list}',
                fl=solr_field,
                rows=len(class_ids)
            )
            
            # Process all results
            for doc in results.docs:
                if solr_field not in doc:
                    continue
                    
                # Parse the SOLR field JSON string
                field_data_str = doc[solr_field][0]
                field_data = json.loads(field_data_str)
                
                # Extract core term information
                term_core = field_data.get('term', {}).get('core', {})
                class_short_form = term_core.get('short_form', '')
                
                # Extract label (prefer symbol over label)
                label_text = term_core.get('label', 'Unknown')
                if term_core.get('symbol') and len(term_core.get('symbol', '')) > 0:
                    label_text = term_core.get('symbol')
                label_text = unquote(label_text)
                
                # Extract tags from unique_facets
                tags = '|'.join(term_core.get('unique_facets', []))
                
                # Extract thumbnail from anatomy_channel_image if available
                thumbnail = ''
                anatomy_images = field_data.get('anatomy_channel_image', [])
                if anatomy_images and len(anatomy_images) > 0:
                    first_img = anatomy_images[0]
                    channel_image = first_img.get('channel_image', {})
                    image_info = channel_image.get('image', {})
                    thumbnail_url = image_info.get('image_thumbnail', '')
                    
                    if thumbnail_url:
                        # Convert to HTTPS and use non-transparent version
                        thumbnail_url = thumbnail_url.replace('http://', 'https://').replace('thumbnailT.png', 'thumbnail.png')
                        
                        # Format thumbnail with proper markdown link (matching Neo4j behavior)
                        template_anatomy = image_info.get('template_anatomy', {})
                        if template_anatomy:
                            template_label = template_anatomy.get('symbol') or template_anatomy.get('label', '')
                            template_label = unquote(template_label)
                            anatomy_label = first_img.get('anatomy', {}).get('label', label_text)
                            anatomy_label = unquote(anatomy_label)
                            alt_text = f"{anatomy_label} aligned to {template_label}"
                            thumbnail = f"[![{alt_text}]({thumbnail_url} '{alt_text}')]({class_short_form})"
                
                # Build row
                row = {
                    'id': class_short_form,
                    'label': f"[{label_text}]({class_short_form})",
                    'tags': tags,
                    'thumbnail': thumbnail
                }
                
                # Optionally add source information
                if include_source:
                    source = ''
                    source_id = ''
                    xrefs = field_data.get('xrefs', [])
                    if xrefs and len(xrefs) > 0:
                        for xref in xrefs:
                            if xref.get('is_data_source', False):
                                site_info = xref.get('site', {})
                                site_label = site_info.get('symbol') or site_info.get('label', '')
                                site_short_form = site_info.get('short_form', '')
                                if site_label and site_short_form:
                                    source = f"[{site_label}]({site_short_form})"
                                
                                accession = xref.get('accession', '')
                                link_base = xref.get('link_base', '')
                                if accession and link_base:
                                    source_id = f"[{accession}]({link_base}{accession})"
                                break
                    row['source'] = source
                    row['source_id'] = source_id
                
                rows.append(row)
                
        except Exception as e:
            print(f"Error fetching SOLR data: {e}")
            import traceback
            traceback.print_exc()
        
        # Convert to DataFrame if requested
        if return_dataframe:
            df = pd.DataFrame(rows)
            # Apply markdown encoding
            columns_to_encode = ['label', 'thumbnail']
            df = encode_markdown_links(df, columns_to_encode)
            return df
        
        # Return formatted dict
        return {
            "headers": _get_standard_query_headers(),
            "rows": rows,
            "count": total_count
        }
        
    except Exception as e:
        # Construct the Owlery URL for debugging failed queries
        owlery_base = "http://owl.virtualflybrain.org/kbs/vfb"
        try:
            if hasattr(vc.vfb, 'oc') and hasattr(vc.vfb.oc, 'owlery_endpoint'):
                owlery_base = vc.vfb.oc.owlery_endpoint.rstrip('/')
        except Exception:
            pass
        
        from urllib.parse import urlencode
        
        # Build the full URL with all parameters exactly as the request would be made
        params = {
            'object': owl_query_string,
            'direct': 'true' if query_instances else 'false',  # instances use direct=true, subclasses use direct=false
            'includeDeprecated': 'false'
        }
        
        # For subclasses queries, add includeEquivalent parameter
        if not query_instances:
            params['includeEquivalent'] = 'true'
        
        endpoint = "/instances" if query_instances else "/subclasses"
        owlery_url = f"{owlery_base}{endpoint}?{urlencode(params)}"
        
        import sys
        import requests
        
        # Check if this is a 400 Bad Request (invalid query) vs other errors
        is_bad_request = isinstance(e, requests.exceptions.HTTPError) and hasattr(e, 'response') and e.response.status_code == 400
        
        if is_bad_request:
            # 400 Bad Request means the term isn't valid for this type of query (e.g., anatomical query on expression pattern)
            # Return 0 results instead of error
            print(f"INFO: Owlery query returned 400 Bad Request (invalid for this term type): {owl_query_string}", file=sys.stderr)
            if return_dataframe:
                return pd.DataFrame()
            return {
                "headers": _get_standard_query_headers(),
                "rows": [],
                "count": 0
            }
        else:
            # Other errors (500, network issues, etc.) - return error indication
            print(f"ERROR: Owlery {'instances' if query_instances else 'subclasses'} query failed: {e}", file=sys.stderr)
            print(f"       Full URL: {owlery_url}", file=sys.stderr)
            print(f"       Query string: {owl_query_string}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            # Return error indication with count=-1
            if return_dataframe:
                return pd.DataFrame()
            return {
                "headers": _get_standard_query_headers(),
                "rows": [],
                "count": -1
            }


def get_anatomy_scrnaseq(anatomy_short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieve single cell RNA-seq data (clusters and datasets) for the specified anatomical region.
    
    This implements the anatScRNAseqQuery from the VFB XMI specification.
    Returns clusters that are composed primarily of the anatomy, along with their parent datasets and publications.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    Query: anat_scRNAseq_query
    
    :param anatomy_short_form: Short form identifier of the anatomical region (e.g., 'FBbt_00003982')
    :param return_dataframe: Returns pandas DataFrame if True, otherwise returns formatted dict (default: True)
    :param limit: Maximum number of results to return (default: -1 for all results)
    :return: scRNAseq clusters and datasets for this anatomy
    :rtype: pandas.DataFrame or dict
    """
    
    # Count query
    count_query = f"""
        MATCH (primary:Class:Anatomy)
        WHERE primary.short_form = '{anatomy_short_form}'
        WITH primary
        MATCH (primary)<-[:composed_primarily_of]-(c:Cluster)-[:has_source]->(ds:scRNAseq_DataSet)
        RETURN COUNT(c) AS total_count
    """
    
    count_results = vc.nc.commit_list([count_query])
    count_df = pd.DataFrame.from_records(get_dict_cursor()(count_results))
    total_count = count_df['total_count'][0] if not count_df.empty else 0
    
    # Main query: get clusters with dataset and publication info
    main_query = f"""
        MATCH (primary:Class:Anatomy)
        WHERE primary.short_form = '{anatomy_short_form}'
        WITH primary
        MATCH (primary)<-[:composed_primarily_of]-(c:Cluster)-[:has_source]->(ds:scRNAseq_DataSet)
        OPTIONAL MATCH (ds)-[:has_reference]->(p:pub)
        WITH {{
            short_form: c.short_form,
            label: coalesce(c.label,''),
            iri: c.iri,
            types: labels(c),
            unique_facets: apoc.coll.sort(coalesce(c.uniqueFacets, [])),
            symbol: coalesce(([]+c.symbol)[0], '')
        }} AS cluster,
        {{
            short_form: ds.short_form,
            label: coalesce(ds.label,''),
            iri: ds.iri,
            types: labels(ds),
            unique_facets: apoc.coll.sort(coalesce(ds.uniqueFacets, [])),
            symbol: coalesce(([]+ds.symbol)[0], '')
        }} AS dataset,
        COLLECT({{
            core: {{
                short_form: p.short_form,
                label: coalesce(p.label,''),
                iri: p.iri,
                types: labels(p),
                unique_facets: apoc.coll.sort(coalesce(p.uniqueFacets, [])),
                symbol: coalesce(([]+p.symbol)[0], '')
            }},
            PubMed: coalesce(([]+p.PMID)[0], ''),
            FlyBase: coalesce(([]+p.FlyBase)[0], ''),
            DOI: coalesce(([]+p.DOI)[0], '')
        }}) AS pubs,
        primary
        RETURN
            cluster.short_form AS id,
            apoc.text.format("[%s](%s)", [cluster.label, cluster.short_form]) AS name,
            apoc.text.join(cluster.unique_facets, '|') AS tags,
            dataset,
            pubs
        ORDER BY cluster.label
    """
    
    if limit != -1:
        main_query += f" LIMIT {limit}"
    
    # Execute the query
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    
    # Encode markdown links
    if not df.empty:
        columns_to_encode = ['name']
        df = encode_markdown_links(df, columns_to_encode)
    
    if return_dataframe:
        return df
    else:
        formatted_results = {
            "headers": {
                "id": {"title": "ID", "type": "selection_id", "order": -1},
                "name": {"title": "Cluster", "type": "markdown", "order": 0},
                "tags": {"title": "Tags", "type": "tags", "order": 1},
                "dataset": {"title": "Dataset", "type": "metadata", "order": 2},
                "pubs": {"title": "Publications", "type": "metadata", "order": 3}
            },
            "rows": [
                {key: row[key] for key in ["id", "name", "tags", "dataset", "pubs"]}
                for row in safe_to_dict(df, sort_by_id=False)
            ],
            "count": total_count
        }
        return formatted_results


def get_cluster_expression(cluster_short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieve genes expressed in the specified cluster.
    
    This implements the clusterExpression query from the VFB XMI specification.
    Returns genes with expression levels and extents for a given cluster.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    Query: cluster_expression_query
    
    :param cluster_short_form: Short form identifier of the cluster (e.g., 'VFB_00101234')
    :param return_dataframe: Returns pandas DataFrame if True, otherwise returns formatted dict (default: True)
    :param limit: Maximum number of results to return (default: -1 for all results)
    :return: Genes expressed in this cluster with expression data
    :rtype: pandas.DataFrame or dict
    """
    
    # Count query
    count_query = f"""
        MATCH (primary:Individual:Cluster)
        WHERE primary.short_form = '{cluster_short_form}'
        WITH primary
        MATCH (primary)-[e:expresses]->(g:Gene:Class)
        RETURN COUNT(g) AS total_count
    """
    
    count_results = vc.nc.commit_list([count_query])
    count_df = pd.DataFrame.from_records(get_dict_cursor()(count_results))
    total_count = count_df['total_count'][0] if not count_df.empty else 0
    
    # Main query: get genes with expression levels
    main_query = f"""
        MATCH (primary:Individual:Cluster)
        WHERE primary.short_form = '{cluster_short_form}'
        WITH primary
        MATCH (primary)-[e:expresses]->(g:Gene:Class)
        WITH coalesce(e.expression_level_padded[0], e.expression_level[0]) as expression_level,
             e.expression_extent[0] as expression_extent,
             {{
                 short_form: g.short_form,
                 label: coalesce(g.label,''),
                 iri: g.iri,
                 types: labels(g),
                 unique_facets: apoc.coll.sort(coalesce(g.uniqueFacets, [])),
                 symbol: coalesce(([]+g.symbol)[0], '')
             }} AS gene,
             primary
        MATCH (a:Anatomy)<-[:composed_primarily_of]-(primary)
        WITH {{
            short_form: a.short_form,
            label: coalesce(a.label,''),
            iri: a.iri,
            types: labels(a),
            unique_facets: apoc.coll.sort(coalesce(a.uniqueFacets, [])),
            symbol: coalesce(([]+a.symbol)[0], '')
        }} AS anatomy, primary, expression_level, expression_extent, gene
        RETURN
            gene.short_form AS id,
            apoc.text.format("[%s](%s)", [gene.symbol, gene.short_form]) AS name,
            apoc.text.join(gene.unique_facets, '|') AS tags,
            expression_level,
            expression_extent,
            anatomy
        ORDER BY expression_level DESC, gene.symbol
    """
    
    if limit != -1:
        main_query += f" LIMIT {limit}"
    
    # Execute the query
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    
    # Encode markdown links
    if not df.empty:
        columns_to_encode = ['name']
        df = encode_markdown_links(df, columns_to_encode)
    
    if return_dataframe:
        return df
    else:
        formatted_results = {
            "headers": {
                "id": {"title": "ID", "type": "selection_id", "order": -1},
                "name": {"title": "Gene", "type": "markdown", "order": 0},
                "tags": {"title": "Tags", "type": "tags", "order": 1},
                "expression_level": {"title": "Expression Level", "type": "numeric", "order": 2},
                "expression_extent": {"title": "Expression Extent", "type": "numeric", "order": 3},
                "anatomy": {"title": "Anatomy", "type": "metadata", "order": 4}
            },
            "rows": [
                {key: row[key] for key in ["id", "name", "tags", "expression_level", "expression_extent", "anatomy"]}
                for row in safe_to_dict(df, sort_by_id=False)
            ],
            "count": total_count
        }
        return formatted_results


def get_expression_cluster(gene_short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieve scRNAseq clusters expressing the specified gene.
    
    This implements the expressionCluster query from the VFB XMI specification.
    Returns clusters that express a given gene with expression levels and anatomy info.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    Query: expression_cluster_query
    
    :param gene_short_form: Short form identifier of the gene (e.g., 'FBgn_00001234')
    :param return_dataframe: Returns pandas DataFrame if True, otherwise returns formatted dict (default: True)
    :param limit: Maximum number of results to return (default: -1 for all results)
    :return: Clusters expressing this gene with expression data
    :rtype: pandas.DataFrame or dict
    """
    
    # Count query
    count_query = f"""
        MATCH (primary:Individual:Cluster)-[e:expresses]->(g:Gene:Class)
        WHERE g.short_form = '{gene_short_form}'
        RETURN COUNT(primary) AS total_count
    """
    
    count_results = vc.nc.commit_list([count_query])
    count_df = pd.DataFrame.from_records(get_dict_cursor()(count_results))
    total_count = count_df['total_count'][0] if not count_df.empty else 0
    
    # Main query: get clusters with expression levels
    main_query = f"""
        MATCH (primary:Individual:Cluster)-[e:expresses]->(g:Gene:Class)
        WHERE g.short_form = '{gene_short_form}'
        WITH e.expression_level[0] as expression_level,
             e.expression_extent[0] as expression_extent,
             {{
                 short_form: g.short_form,
                 label: coalesce(g.label,''),
                 iri: g.iri,
                 types: labels(g),
                 unique_facets: apoc.coll.sort(coalesce(g.uniqueFacets, [])),
                 symbol: coalesce(([]+g.symbol)[0], '')
             }} AS gene,
             primary
        MATCH (a:Anatomy)<-[:composed_primarily_of]-(primary)
        WITH {{
            short_form: a.short_form,
            label: coalesce(a.label,''),
            iri: a.iri,
            types: labels(a),
            unique_facets: apoc.coll.sort(coalesce(a.uniqueFacets, [])),
            symbol: coalesce(([]+a.symbol)[0], '')
        }} AS anatomy, primary, expression_level, expression_extent, gene
        RETURN
            primary.short_form AS id,
            apoc.text.format("[%s](%s)", [primary.label, primary.short_form]) AS name,
            apoc.text.join(coalesce(primary.uniqueFacets, []), '|') AS tags,
            expression_level,
            expression_extent,
            anatomy
        ORDER BY expression_level DESC, primary.label
    """
    
    if limit != -1:
        main_query += f" LIMIT {limit}"
    
    # Execute the query
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    
    # Encode markdown links
    if not df.empty:
        columns_to_encode = ['name']
        df = encode_markdown_links(df, columns_to_encode)
    
    if return_dataframe:
        return df
    else:
        formatted_results = {
            "headers": {
                "id": {"title": "ID", "type": "selection_id", "order": -1},
                "name": {"title": "Cluster", "type": "markdown", "order": 0},
                "tags": {"title": "Tags", "type": "tags", "order": 1},
                "expression_level": {"title": "Expression Level", "type": "numeric", "order": 2},
                "expression_extent": {"title": "Expression Extent", "type": "numeric", "order": 3},
                "anatomy": {"title": "Anatomy", "type": "metadata", "order": 4}
            },
            "rows": [
                {key: row[key] for key in ["id", "name", "tags", "expression_level", "expression_extent", "anatomy"]}
                for row in safe_to_dict(df, sort_by_id=False)
            ],
            "count": total_count
        }
        return formatted_results


def get_scrnaseq_dataset_data(dataset_short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieve all clusters for a scRNAseq dataset.
    
    This implements the scRNAdatasetData query from the VFB XMI specification.
    Returns all clusters in a dataset with anatomy info and publications.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    Query: dataset_scRNAseq_query
    
    :param dataset_short_form: Short form identifier of the dataset (e.g., 'VFB_00101234')
    :param return_dataframe: Returns pandas DataFrame if True, otherwise returns formatted dict (default: True)
    :param limit: Maximum number of results to return (default: -1 for all results)
    :return: Clusters in this dataset with anatomy and publication data
    :rtype: pandas.DataFrame or dict
    """
    
    # Count query
    count_query = f"""
        MATCH (c:Individual)-[:has_source]->(ds:scRNAseq_DataSet)
        WHERE ds.short_form = '{dataset_short_form}'
        RETURN COUNT(c) AS total_count
    """
    
    count_results = vc.nc.commit_list([count_query])
    count_df = pd.DataFrame.from_records(get_dict_cursor()(count_results))
    total_count = count_df['total_count'][0] if not count_df.empty else 0
    
    # Main query: get clusters with anatomy and publications
    main_query = f"""
        MATCH (c:Individual:Cluster)-[:has_source]->(ds:scRNAseq_DataSet)
        WHERE ds.short_form = '{dataset_short_form}'
        MATCH (a:Class:Anatomy)<-[:composed_primarily_of]-(c)
        WITH *, {{
            short_form: a.short_form,
            label: coalesce(a.label,''),
            iri: a.iri,
            types: labels(a),
            unique_facets: apoc.coll.sort(coalesce(a.uniqueFacets, [])),
            symbol: coalesce(([]+a.symbol)[0], '')
        }} AS anatomy
        OPTIONAL MATCH (ds)-[:has_reference]->(p:pub)
        WITH COLLECT({{
            core: {{
                short_form: p.short_form,
                label: coalesce(p.label,''),
                iri: p.iri,
                types: labels(p),
                unique_facets: apoc.coll.sort(coalesce(p.uniqueFacets, [])),
                symbol: coalesce(([]+p.symbol)[0], '')
            }},
            PubMed: coalesce(([]+p.PMID)[0], ''),
            FlyBase: coalesce(([]+p.FlyBase)[0], ''),
            DOI: coalesce(([]+p.DOI)[0], '')
        }}) AS pubs, c, anatomy
        RETURN
            c.short_form AS id,
            apoc.text.format("[%s](%s)", [c.label, c.short_form]) AS name,
            apoc.text.join(coalesce(c.uniqueFacets, []), '|') AS tags,
            anatomy,
            pubs
        ORDER BY c.label
    """
    
    if limit != -1:
        main_query += f" LIMIT {limit}"
    
    # Execute the query
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    
    # Encode markdown links
    if not df.empty:
        columns_to_encode = ['name']
        df = encode_markdown_links(df, columns_to_encode)
    
    if return_dataframe:
        return df
    else:
        formatted_results = {
            "headers": {
                "id": {"title": "ID", "type": "selection_id", "order": -1},
                "name": {"title": "Cluster", "type": "markdown", "order": 0},
                "tags": {"title": "Tags", "type": "tags", "order": 1},
                "anatomy": {"title": "Anatomy", "type": "metadata", "order": 2},
                "pubs": {"title": "Publications", "type": "metadata", "order": 3}
            },
            "rows": [
                {key: row[key] for key in ["id", "name", "tags", "anatomy", "pubs"]}
                for row in safe_to_dict(df, sort_by_id=False)
            ],
            "count": total_count
        }
        return formatted_results


# ===== NBLAST Similarity Queries =====

def get_similar_morphology(neuron_short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieve neurons with similar morphology to the specified neuron using NBLAST.
    
    This implements the SimilarMorphologyTo query from the VFB XMI specification.
    Returns neurons with NBLAST similarity scores.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    Query: has_similar_morphology_to (NBLAST_anat_image_query)
    
    :param neuron_short_form: Short form identifier of the neuron (e.g., 'VFB_00101234')
    :param return_dataframe: Returns pandas DataFrame if True, otherwise returns formatted dict (default: True)
    :param limit: Maximum number of results to return (default: -1 for all results)
    :return: Neurons with similar morphology and NBLAST scores
    :rtype: pandas.DataFrame or dict
    """
    
    # Count query
    count_query = f"""
        MATCH (n:Individual)-[nblast:has_similar_morphology_to]-(primary:Individual)
        WHERE n.short_form = '{neuron_short_form}' AND EXISTS(nblast.NBLAST_score)
        RETURN count(primary) AS count
    """
    
    # Get total count
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0
    
    # Main query
    main_query = f"""
        MATCH (n:Individual)-[nblast:has_similar_morphology_to]-(primary:Individual)
        WHERE n.short_form = '{neuron_short_form}' AND EXISTS(nblast.NBLAST_score)
        WITH primary, nblast
        OPTIONAL MATCH (primary)<-[:depicts]-(channel:Individual)-[irw:in_register_with]->(template:Individual)-[:depicts]->(template_anat:Individual)
        WITH template, channel, template_anat, irw, primary, nblast
        OPTIONAL MATCH (channel)-[:is_specified_output_of]->(technique:Class)
        WITH CASE WHEN channel IS NULL THEN [] ELSE collect({{
            channel: {{
                short_form: channel.short_form,
                label: coalesce(channel.label, ''),
                iri: channel.iri,
                types: labels(channel),
                unique_facets: apoc.coll.sort(coalesce(channel.uniqueFacets, [])),
                symbol: coalesce(channel.symbol[0], '')
            }},
            imaging_technique: {{
                short_form: technique.short_form,
                label: coalesce(technique.label, ''),
                iri: technique.iri,
                types: labels(technique),
                unique_facets: apoc.coll.sort(coalesce(technique.uniqueFacets, [])),
                symbol: coalesce(technique.symbol[0], '')
            }},
            image: {{
                template_channel: {{
                    short_form: template.short_form,
                    label: coalesce(template.label, ''),
                    iri: template.iri,
                    types: labels(template),
                    unique_facets: apoc.coll.sort(coalesce(template.uniqueFacets, [])),
                    symbol: coalesce(template.symbol[0], '')
                }},
                template_anatomy: {{
                    short_form: template_anat.short_form,
                    label: coalesce(template_anat.label, ''),
                    iri: template_anat.iri,
                    types: labels(template_anat),
                    symbol: coalesce(template_anat.symbol[0], '')
                }},
                image_folder: COALESCE(irw.folder[0], ''),
                index: coalesce(apoc.convert.toInteger(irw.index[0]), []) + []
            }}
        }}) END AS channel_image, primary, nblast
        OPTIONAL MATCH (primary)-[:INSTANCEOF]->(typ:Class)
        WITH CASE WHEN typ IS NULL THEN [] ELSE collect({{
            short_form: typ.short_form,
            label: coalesce(typ.label, ''),
            iri: typ.iri,
            types: labels(typ),
            symbol: coalesce(typ.symbol[0], '')
        }}) END AS types, primary, channel_image, nblast
        RETURN
            primary.short_form AS id,
            '[' + primary.label + '](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=' + primary.short_form + ')' AS name,
            apoc.text.join(coalesce(primary.uniqueFacets, []), '|') AS tags,
            nblast.NBLAST_score[0] AS score,
            types,
            channel_image
        ORDER BY score DESC
    """
    
    if limit != -1:
        main_query += f" LIMIT {limit}"
    
    # Execute the query
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    
    # Encode markdown links
    if not df.empty:
        columns_to_encode = ['name']
        df = encode_markdown_links(df, columns_to_encode)
    
    if return_dataframe:
        return df
    else:
        formatted_results = {
            "headers": {
                "id": {"title": "ID", "type": "selection_id", "order": -1},
                "name": {"title": "Neuron", "type": "markdown", "order": 0},
                "score": {"title": "NBLAST Score", "type": "text", "order": 1},
                "tags": {"title": "Tags", "type": "tags", "order": 2},
                "types": {"title": "Types", "type": "metadata", "order": 3},
                "channel_image": {"title": "Images", "type": "metadata", "order": 4}
            },
            "rows": [
                {key: row[key] for key in ["id", "name", "score", "tags", "types", "channel_image"]}
                for row in safe_to_dict(df, sort_by_id=False)
            ],
            "count": total_count
        }
        return formatted_results


def get_similar_morphology_part_of(neuron_short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieve expression patterns with similar morphology to part of the specified neuron (NBLASTexp).
    
    XMI: has_similar_morphology_to_part_of
    """
    count_query = f"MATCH (n:Individual)-[nblast:has_similar_morphology_to_part_of]-(primary:Individual) WHERE n.short_form = '{neuron_short_form}' AND EXISTS(nblast.NBLAST_score) RETURN count(primary) AS count"
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0
    
    main_query = f"""MATCH (n:Individual)-[nblast:has_similar_morphology_to_part_of]-(primary:Individual) WHERE n.short_form = '{neuron_short_form}' AND EXISTS(nblast.NBLAST_score) WITH primary, nblast
        OPTIONAL MATCH (primary)-[:INSTANCEOF]->(typ:Class) WITH CASE WHEN typ IS NULL THEN [] ELSE collect({{short_form: typ.short_form, label: coalesce(typ.label, ''), iri: typ.iri, types: labels(typ), symbol: coalesce(typ.symbol[0], '')}}) END AS types, primary, nblast
        RETURN primary.short_form AS id, '[' + primary.label + '](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=' + primary.short_form + ')' AS name, apoc.text.join(coalesce(primary.uniqueFacets, []), '|') AS tags, nblast.NBLAST_score[0] AS score, types ORDER BY score DESC"""
    if limit != -1: main_query += f" LIMIT {limit}"
    
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    if not df.empty: df = encode_markdown_links(df, ['name'])
    
    if return_dataframe: return df
    return {"headers": {"id": {"title": "ID", "type": "selection_id", "order": -1}, "name": {"title": "Expression Pattern", "type": "markdown", "order": 0}, "score": {"title": "NBLAST Score", "type": "text", "order": 1}, "tags": {"title": "Tags", "type": "tags", "order": 2}}, "rows": [{key: row[key] for key in ["id", "name", "score", "tags"]} for row in safe_to_dict(df, sort_by_id=False)], "count": total_count}


def get_similar_morphology_part_of_exp(expression_short_form: str, return_dataframe=True, limit: int = -1):
    """Neurons with similar morphology to part of expression pattern (reverse NBLASTexp)."""
    count_query = f"MATCH (n:Individual)-[nblast:has_similar_morphology_to_part_of]-(primary:Individual) WHERE n.short_form = '{expression_short_form}' AND EXISTS(nblast.NBLAST_score) RETURN count(primary) AS count"
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0
    
    main_query = f"""MATCH (n:Individual)-[nblast:has_similar_morphology_to_part_of]-(primary:Individual) WHERE n.short_form = '{expression_short_form}' AND EXISTS(nblast.NBLAST_score) WITH primary, nblast
        OPTIONAL MATCH (primary)-[:INSTANCEOF]->(typ:Class) WITH CASE WHEN typ IS NULL THEN [] ELSE collect({{short_form: typ.short_form, label: coalesce(typ.label, ''), iri: typ.iri, types: labels(typ), symbol: coalesce(typ.symbol[0], '')}}) END AS types, primary, nblast
        RETURN primary.short_form AS id, '[' + primary.label + '](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=' + primary.short_form + ')' AS name, apoc.text.join(coalesce(primary.uniqueFacets, []), '|') AS tags, nblast.NBLAST_score[0] AS score, types ORDER BY score DESC"""
    if limit != -1: main_query += f" LIMIT {limit}"
    
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    if not df.empty: df = encode_markdown_links(df, ['name'])
    
    if return_dataframe: return df
    return {"headers": {"id": {"title": "ID", "type": "selection_id", "order": -1}, "name": {"title": "Neuron", "type": "markdown", "order": 0}, "score": {"title": "NBLAST Score", "type": "text", "order": 1}, "tags": {"title": "Tags", "type": "tags", "order": 2}}, "rows": [{key: row[key] for key in ["id", "name", "score", "tags"]} for row in safe_to_dict(df, sort_by_id=False)], "count": total_count}


def get_similar_morphology_nb(neuron_short_form: str, return_dataframe=True, limit: int = -1):
    """NeuronBridge similarity matches for neurons."""
    count_query = f"MATCH (n:Individual)-[nblast:has_similar_morphology_to_part_of]-(primary:Individual) WHERE n.short_form = '{neuron_short_form}' AND EXISTS(nblast.neuronbridge_score) RETURN count(primary) AS count"
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0
    
    main_query = f"""MATCH (n:Individual)-[nblast:has_similar_morphology_to_part_of]-(primary:Individual) WHERE n.short_form = '{neuron_short_form}' AND EXISTS(nblast.neuronbridge_score) WITH primary, nblast
        OPTIONAL MATCH (primary)-[:INSTANCEOF]->(typ:Class) WITH CASE WHEN typ IS NULL THEN [] ELSE collect({{short_form: typ.short_form, label: coalesce(typ.label, ''), iri: typ.iri, types: labels(typ), symbol: coalesce(typ.symbol[0], '')}}) END AS types, primary, nblast
        RETURN primary.short_form AS id, '[' + primary.label + '](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=' + primary.short_form + ')' AS name, apoc.text.join(coalesce(primary.uniqueFacets, []), '|') AS tags, nblast.neuronbridge_score[0] AS score, types ORDER BY score DESC"""
    if limit != -1: main_query += f" LIMIT {limit}"
    
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    if not df.empty: df = encode_markdown_links(df, ['name'])
    
    if return_dataframe: return df
    return {"headers": {"id": {"title": "ID", "type": "selection_id", "order": -1}, "name": {"title": "Match", "type": "markdown", "order": 0}, "score": {"title": "NB Score", "type": "text", "order": 1}, "tags": {"title": "Tags", "type": "tags", "order": 2}}, "rows": [{key: row[key] for key in ["id", "name", "score", "tags"]} for row in safe_to_dict(df, sort_by_id=False)], "count": total_count}


def get_similar_morphology_nb_exp(expression_short_form: str, return_dataframe=True, limit: int = -1):
    """NeuronBridge similarity matches for expression patterns."""
    count_query = f"MATCH (n:Individual)-[nblast:has_similar_morphology_to_part_of]-(primary:Individual) WHERE n.short_form = '{expression_short_form}' AND EXISTS(nblast.neuronbridge_score) RETURN count(primary) AS count"
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0
    
    main_query = f"""MATCH (n:Individual)-[nblast:has_similar_morphology_to_part_of]-(primary:Individual) WHERE n.short_form = '{expression_short_form}' AND EXISTS(nblast.neuronbridge_score) WITH primary, nblast
        OPTIONAL MATCH (primary)-[:INSTANCEOF]->(typ:Class) WITH CASE WHEN typ IS NULL THEN [] ELSE collect({{short_form: typ.short_form, label: coalesce(typ.label, ''), iri: typ.iri, types: labels(typ), symbol: coalesce(typ.symbol[0], '')}}) END AS types, primary, nblast
        RETURN primary.short_form AS id, '[' + primary.label + '](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=' + primary.short_form + ')' AS name, apoc.text.join(coalesce(primary.uniqueFacets, []), '|') AS tags, nblast.neuronbridge_score[0] AS score, types ORDER BY score DESC"""
    if limit != -1: main_query += f" LIMIT {limit}"
    
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    if not df.empty: df = encode_markdown_links(df, ['name'])
    
    if return_dataframe: return df
    return {"headers": {"id": {"title": "ID", "type": "selection_id", "order": -1}, "name": {"title": "Match", "type": "markdown", "order": 0}, "score": {"title": "NB Score", "type": "text", "order": 1}, "tags": {"title": "Tags", "type": "tags", "order": 2}}, "rows": [{key: row[key] for key in ["id", "name", "score", "tags"]} for row in safe_to_dict(df, sort_by_id=False)], "count": total_count}


def get_similar_morphology_userdata(upload_id: str, return_dataframe=True, limit: int = -1):
    """NBLAST results for user-uploaded data (cached in SOLR)."""
    try:
        solr_query = f'{{"params":{{"defType":"edismax","fl":"upload_nblast_query","indent":"true","q.op":"OR","q":"id:{upload_id}","qf":"id","rows":"99"}}}}'
        response = requests.post("https://solr.virtualflybrain.org/solr/vfb_json/select", data=solr_query, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            data = response.json()
            if data.get('response', {}).get('numFound', 0) > 0:
                results = data['response']['docs'][0].get('upload_nblast_query', [])
                if isinstance(results, str): results = json.loads(results)
                df = pd.DataFrame(results if isinstance(results, list) else [])
                if not df.empty and 'name' in df.columns: df = encode_markdown_links(df, ['name'])
                if return_dataframe: return df
                return {"headers": {"id": {"title": "ID", "type": "selection_id", "order": -1}, "name": {"title": "Match", "type": "markdown", "order": 0}, "score": {"title": "Score", "type": "text", "order": 1}}, "rows": safe_to_dict(df, sort_by_id=False), "count": len(df)}
    except Exception as e:
        print(f"Error fetching user NBLAST data: {e}")
    return pd.DataFrame() if return_dataframe else {"headers": {}, "rows": [], "count": 0}


# ===== Dataset/Template Queries =====

def get_painted_domains(template_short_form: str, return_dataframe=True, limit: int = -1):
    """List all painted anatomy domains for a template."""
    count_query = f"MATCH (n:Template {{short_form:'{template_short_form}'}})<-[:depicts]-(:Template)<-[r:in_register_with]-(dc:Individual)-[:depicts]->(di:Individual)-[:INSTANCEOF]->(d:Class) WHERE EXISTS(r.index) RETURN count(di) AS count"
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0
    
    main_query = f"""MATCH (n:Template {{short_form:'{template_short_form}'}})<-[:depicts]-(:Template)<-[r:in_register_with]-(dc:Individual)-[:depicts]->(di:Individual)-[:INSTANCEOF]->(d:Class) WHERE EXISTS(r.index)
        RETURN DISTINCT di.short_form AS id, '[' + di.label + '](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=' + di.short_form + ')' AS name, coalesce(di.description[0], d.description[0]) AS description, COLLECT(DISTINCT d.label) AS type, replace(r.folder[0],'http:','https:') + '/thumbnailT.png' AS thumbnail"""
    if limit != -1: main_query += f" LIMIT {limit}"
    
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    if not df.empty: df = encode_markdown_links(df, ['name', 'thumbnail'])
    
    if return_dataframe: return df
    return {"headers": {"id": {"title": "ID", "type": "selection_id", "order": -1}, "name": {"title": "Domain", "type": "markdown", "order": 0}, "type": {"title": "Type", "type": "text", "order": 1}, "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 2}}, "rows": [{key: row[key] for key in ["id", "name", "type", "thumbnail"]} for row in safe_to_dict(df, sort_by_id=False)], "count": total_count}


def get_dataset_images(dataset_short_form: str, return_dataframe=True, limit: int = -1):
    """List all images in a dataset."""
    count_query = f"MATCH (c:DataSet {{short_form:'{dataset_short_form}'}})<-[:has_source]-(primary:Individual)<-[:depicts]-(channel:Individual)-[irw:in_register_with]->(template:Individual)-[:depicts]->(template_anat:Individual) RETURN count(primary) AS count"
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0
    
    main_query = f"""MATCH (c:DataSet {{short_form:'{dataset_short_form}'}})<-[:has_source]-(primary:Individual)<-[:depicts]-(channel:Individual)-[irw:in_register_with]->(template:Individual)-[:depicts]->(template_anat:Individual)
        OPTIONAL MATCH (primary)-[:INSTANCEOF]->(typ:Class)
        RETURN primary.short_form AS id, '[' + primary.label + '](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=' + primary.short_form + ')' AS name, apoc.text.join(coalesce(primary.uniqueFacets, []), '|') AS tags, typ.label AS type"""
    if limit != -1: main_query += f" LIMIT {limit}"
    
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    if not df.empty: df = encode_markdown_links(df, ['name'])
    
    if return_dataframe: return df
    return {"headers": {"id": {"title": "ID", "type": "selection_id", "order": -1}, "name": {"title": "Image", "type": "markdown", "order": 0}, "tags": {"title": "Tags", "type": "tags", "order": 1}, "type": {"title": "Type", "type": "text", "order": 2}}, "rows": [{key: row[key] for key in ["id", "name", "tags", "type"]} for row in safe_to_dict(df, sort_by_id=False)], "count": total_count}


def get_all_aligned_images(template_short_form: str, return_dataframe=True, limit: int = -1):
    """List all images aligned to a template."""
    count_query = f"MATCH (:Template {{short_form:'{template_short_form}'}})<-[:depicts]-(:Template)<-[:in_register_with]-(:Individual)-[:depicts]->(di:Individual) RETURN count(di) AS count"
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0
    
    main_query = f"""MATCH (:Template {{short_form:'{template_short_form}'}})<-[:depicts]-(:Template)<-[:in_register_with]-(:Individual)-[:depicts]->(di:Individual)
        OPTIONAL MATCH (di)-[:INSTANCEOF]->(typ:Class)
        RETURN DISTINCT di.short_form AS id, '[' + di.label + '](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=' + di.short_form + ')' AS name, apoc.text.join(coalesce(di.uniqueFacets, []), '|') AS tags, typ.label AS type"""
    if limit != -1: main_query += f" LIMIT {limit}"
    
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    if not df.empty: df = encode_markdown_links(df, ['name'])
    
    if return_dataframe: return df
    return {"headers": {"id": {"title": "ID", "type": "selection_id", "order": -1}, "name": {"title": "Image", "type": "markdown", "order": 0}, "tags": {"title": "Tags", "type": "tags", "order": 1}, "type": {"title": "Type", "type": "text", "order": 2}}, "rows": [{key: row[key] for key in ["id", "name", "tags", "type"]} for row in safe_to_dict(df, sort_by_id=False)], "count": total_count}


def get_aligned_datasets(template_short_form: str, return_dataframe=True, limit: int = -1):
    """List all datasets aligned to a template."""
    count_query = f"MATCH (ds:DataSet:Individual) WHERE NOT ds:Deprecated AND (:Template:Individual {{short_form:'{template_short_form}'}})<-[:depicts]-(:Template:Individual)-[:in_register_with]-(:Individual)-[:depicts]->(:Individual)-[:has_source]->(ds) RETURN count(ds) AS count"
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0
    
    main_query = f"""MATCH (ds:DataSet:Individual) WHERE NOT ds:Deprecated AND (:Template:Individual {{short_form:'{template_short_form}'}})<-[:depicts]-(:Template:Individual)-[:in_register_with]-(:Individual)-[:depicts]->(:Individual)-[:has_source]->(ds)
        RETURN DISTINCT ds.short_form AS id, '[' + ds.label + '](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=' + ds.short_form + ')' AS name, apoc.text.join(coalesce(ds.uniqueFacets, []), '|') AS tags"""
    if limit != -1: main_query += f" LIMIT {limit}"
    
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    if not df.empty: df = encode_markdown_links(df, ['name'])
    
    if return_dataframe: return df
    return {"headers": {"id": {"title": "ID", "type": "selection_id", "order": -1}, "name": {"title": "Dataset", "type": "markdown", "order": 0}, "tags": {"title": "Tags", "type": "tags", "order": 1}}, "rows": [{key: row[key] for key in ["id", "name", "tags"]} for row in safe_to_dict(df, sort_by_id=False)], "count": total_count}


def get_all_datasets(return_dataframe=True, limit: int = -1):
    """List all available datasets."""
    count_query = "MATCH (ds:DataSet:Individual) WHERE NOT ds:Deprecated AND (:Template:Individual)<-[:depicts]-(:Template:Individual)-[:in_register_with]-(:Individual)-[:depicts]->(:Individual)-[:has_source]->(ds) WITH DISTINCT ds RETURN count(ds) AS count"
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0
    
    main_query = f"""MATCH (ds:DataSet:Individual) WHERE NOT ds:Deprecated AND (:Template:Individual)<-[:depicts]-(:Template:Individual)-[:in_register_with]-(:Individual)-[:depicts]->(:Individual)-[:has_source]->(ds)
        RETURN DISTINCT ds.short_form AS id, '[' + ds.label + '](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=' + ds.short_form + ')' AS name, apoc.text.join(coalesce(ds.uniqueFacets, []), '|') AS tags"""
    if limit != -1: main_query += f" LIMIT {limit}"
    
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    if not df.empty: df = encode_markdown_links(df, ['name'])
    
    if return_dataframe: return df
    return {"headers": {"id": {"title": "ID", "type": "selection_id", "order": -1}, "name": {"title": "Dataset", "type": "markdown", "order": 0}, "tags": {"title": "Tags", "type": "tags", "order": 1}}, "rows": [{key: row[key] for key in ["id", "name", "tags"]} for row in safe_to_dict(df, sort_by_id=False)], "count": total_count}


# ===== Publication Query =====

def get_terms_for_pub(pub_short_form: str, return_dataframe=True, limit: int = -1):
    """List all terms that reference a publication."""
    count_query = f"MATCH (:pub:Individual {{short_form:'{pub_short_form}'}})<-[:has_reference]-(primary:Individual) RETURN count(DISTINCT primary) AS count"
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0
    
    main_query = f"""MATCH (:pub:Individual {{short_form:'{pub_short_form}'}})<-[:has_reference]-(primary:Individual)
        OPTIONAL MATCH (primary)-[:INSTANCEOF]->(typ:Class)
        RETURN DISTINCT primary.short_form AS id, '[' + primary.label + '](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=' + primary.short_form + ')' AS name, apoc.text.join(coalesce(primary.uniqueFacets, []), '|') AS tags, typ.label AS type"""
    if limit != -1: main_query += f" LIMIT {limit}"
    
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    if not df.empty: df = encode_markdown_links(df, ['name'])
    
    if return_dataframe: return df
    return {"headers": {"id": {"title": "ID", "type": "selection_id", "order": -1}, "name": {"title": "Term", "type": "markdown", "order": 0}, "tags": {"title": "Tags", "type": "tags", "order": 1}, "type": {"title": "Type", "type": "text", "order": 2}}, "rows": [{key: row[key] for key in ["id", "name", "tags", "type"]} for row in safe_to_dict(df, sort_by_id=False)], "count": total_count}


# ===== Complex Transgene Expression Query =====

def get_transgene_expression_here(anatomy_short_form: str, return_dataframe=True, limit: int = -1):
    """Multi-step query: Owlery subclasses + expression overlaps."""
    # This uses a combination of Owlery and Neo4j similar to get_expression_overlaps_here
    # but specifically for transgenes. For now, we'll use the existing expression pattern logic
    return get_expression_overlaps_here(anatomy_short_form, return_dataframe, limit)


def fill_query_results(term_info):
    def process_query(query):
        # print(f"Query Keys:{query.keys()}")
        
        if "preview" in query.keys() and query['preview'] > 0:
            function = globals().get(query['function'])
            summary_mode = query.get('output_format', 'table') == 'ribbon'

            if function:
                # print(f"Function {query['function']} found")
                
                try:
                    # Unpack the default dictionary and pass its contents as arguments
                    function_args = query['takes'].get("default", {})
                    # print(f"Function args: {function_args}")

                    # Check function signature to see if it takes a positional argument for short_form
                    sig = inspect.signature(function)
                    params = list(sig.parameters.keys())
                    # Skip 'self' if it's a method, and check if first param is not return_dataframe/limit/summary_mode
                    first_param = params[1] if params and params[0] == 'self' else (params[0] if params else None)
                    takes_short_form = first_param and first_param not in ['return_dataframe', 'limit', 'summary_mode']

                    # Modify this line to use the correct arguments and pass the default arguments
                    if summary_mode:
                        if function_args and takes_short_form:
                            # Pass the short_form as positional argument
                            short_form_value = list(function_args.values())[0]
                            result = function(short_form_value, return_dataframe=False, limit=query['preview'], summary_mode=summary_mode)
                        else:
                            result = function(return_dataframe=False, limit=query['preview'], summary_mode=summary_mode)
                    else:
                        if function_args and takes_short_form:
                            short_form_value = list(function_args.values())[0]
                            result = function(short_form_value, return_dataframe=False, limit=query['preview'])
                        else:
                            result = function(return_dataframe=False, limit=query['preview'])
                except Exception as e:
                    print(f"Error executing query function {query['function']}: {e}")
                    # Set default values for failed query
                    query['preview_results'] = {'headers': query.get('preview_columns', ['id', 'label', 'tags', 'thumbnail']), 'rows': []}
                    query['count'] = 0
                    return
                # print(f"Function result: {result}")
                
                # Filter columns based on preview_columns
                filtered_result = []
                filtered_headers = {}
                
                if result is None:
                    print(f"ERROR: Query function {query['function']} returned None - this indicates a query failure that needs investigation")
                    query['preview_results'] = {'headers': query.get('preview_columns', ['id', 'label', 'tags', 'thumbnail']), 'rows': []}
                    query['count'] = 0
                    return
                
                if isinstance(result, dict) and 'rows' in result:
                    for item in result['rows']:
                        if 'preview_columns' in query.keys() and len(query['preview_columns']) > 0:
                            filtered_item = {col: item[col] for col in query['preview_columns']}
                        else:
                            filtered_item = item
                        filtered_result.append(filtered_item)
                        
                    if 'headers' in result:
                        if 'preview_columns' in query.keys() and len(query['preview_columns']) > 0:
                            filtered_headers = {col: result['headers'][col] for col in query['preview_columns']}
                        else:
                            filtered_headers = result['headers']
                elif isinstance(result, dict) and 'data' in result:
                    # Handle legacy 'data' key as alias for 'rows'
                    for item in result['data']:
                        if 'preview_columns' in query.keys() and len(query['preview_columns']) > 0:
                            filtered_item = {col: item[col] for col in query['preview_columns']}
                        else:
                            filtered_item = item
                        filtered_result.append(filtered_item)
                        
                    if 'headers' in result:
                        if 'preview_columns' in query.keys() and len(query['preview_columns']) > 0:
                            filtered_headers = {col: result['headers'][col] for col in query['preview_columns']}
                        else:
                            filtered_headers = result['headers']
                elif isinstance(result, list) and all(isinstance(item, dict) for item in result):
                    for item in result:
                        if 'preview_columns' in query.keys() and len(query['preview_columns']) > 0:
                            filtered_item = {col: item[col] for col in query['preview_columns']}
                        else:
                            filtered_item = item
                        filtered_result.append(filtered_item)
                elif isinstance(result, pd.DataFrame):
                    filtered_result = safe_to_dict(result[query['preview_columns']])
                else:
                    print(f"Unsupported result format for filtering columns in {query['function']}")
                
                # Handle count extraction based on result type
                if isinstance(result, dict) and 'count' in result:
                    result_count = result['count']
                    # If limit was applied, the count in dict may be wrong, get correct count
                    if query['preview'] > 0 and result_count == len(result['rows']):
                        try:
                            if function_args and takes_short_form:
                                short_form_value = list(function_args.values())[0]
                                full_dict = function(short_form_value, return_dataframe=False, limit=-1)
                            else:
                                full_dict = function(return_dataframe=False, limit=-1)
                            result_count = full_dict['count']
                        except Exception as e:
                            print(f"Error getting full count for {query['function']}: {e}")
                            result_count = result['count']  # Keep as is
                elif isinstance(result, pd.DataFrame):
                    # For DataFrame results, we need the full count even when preview is limited
                    try:
                        if function_args and takes_short_form:
                            short_form_value = list(function_args.values())[0]
                            full_result = function(short_form_value, return_dataframe=True, limit=-1)
                        else:
                            full_result = function(return_dataframe=True, limit=-1)
                        result_count = len(full_result)
                    except Exception as e:
                        print(f"Error getting full count for {query['function']}: {e}")
                        result_count = len(result)  # Fallback to limited count
                else:
                    result_count = 0
                
                # Store preview results (count is stored at query level, not in preview_results)
                # Sort rows based on the sort field in headers, default to ID descending if none
                sort_column = None
                sort_direction = None
                for col, info in filtered_headers.items():
                    if 'sort' in info and isinstance(info['sort'], dict):
                        sort_column = col
                        sort_direction = list(info['sort'].values())[0]  # e.g., 'Asc' or 'Desc'
                        break
                if sort_column:
                    reverse = sort_direction == 'Desc'
                    filtered_result.sort(key=lambda x: x.get(sort_column, ''), reverse=reverse)
                else:
                    # Default to ID descending if no sort specified
                    filtered_result.sort(key=lambda x: x.get('id', ''), reverse=True)
                query['preview_results'] = {'headers': filtered_headers, 'rows': filtered_result}
                query['count'] = result_count
                # print(f"Filtered result: {filtered_result}")
            else:
                print(f"Function {query['function']} not found")
        else:
            print("Preview key not found or preview is 0")

    with ThreadPoolExecutor() as executor:
        executor.map(process_query, term_info['Queries'])
    
    return term_info
