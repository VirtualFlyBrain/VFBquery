import pysolr
from .term_info_queries import deserialize_term_info
# Replace VfbConnect import with our new SolrTermInfoFetcher
from .solr_fetcher import SolrTermInfoFetcher
# Keep dict_cursor if it's used elsewhere - lazy import to avoid GUI issues
from marshmallow import Schema, fields, post_load
from typing import List, Tuple, Dict, Any, Union
import pandas as pd
from marshmallow import ValidationError
import json

# Lazy import for dict_cursor to avoid GUI library issues
def get_dict_cursor():
    """Lazy import dict_cursor to avoid import issues during testing"""
    try:
        from vfb_connect.cross_server_tools import dict_cursor
        return dict_cursor
    except ImportError as e:
        raise ImportError(f"vfb_connect is required but could not be imported: {e}")

# Connect to the VFB SOLR server
vfb_solr = pysolr.Solr('http://solr.virtualflybrain.org/solr/vfb_json/', always_commit=False, timeout=990)

# Replace VfbConnect with SolrTermInfoFetcher
vc = SolrTermInfoFetcher()

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
    Encodes brackets in the given text.

    :param text: The text to encode.
    :return: The text with brackets encoded.
    """
    return (text.replace('(', '%28')
                .replace(')', '%29')
                .replace('[', '%5B')
                .replace(']', '%5D'))

def encode_markdown_links(df, columns):
    """
    Encodes brackets in the labels and titles within markdown links and images, leaving the link syntax intact.
    :param df: DataFrame containing the query results.
    :param columns: List of column names to apply encoding to.
    """
    def encode_label(label):
        if not isinstance(label, str):
            return label
            
        try:
            # Process linked images (format: [![alt text](image_url "title")](link))
            if label.startswith("[!["):
                # Split into image part and link part
                parts = label.split(")](")
                if len(parts) < 2:
                    return label
                
                image_part = parts[0]
                link_part = parts[1]
                
                # Process the image part
                image_parts = image_part.split("](")
                if len(image_parts) < 2:
                    return label
                
                alt_text = image_parts[0][3:]  # Remove the "[![" prefix
                # Encode brackets in alt text
                alt_text_encoded = encode_brackets(alt_text)
                
                # Reconstruct the linked image with encoded alt text
                encoded_label = f"[![{alt_text_encoded}]({image_parts[1]})]({link_part}"
                return encoded_label
            
            # Process regular markdown links
            elif label.startswith("[") and "](" in label:
                parts = label.split("](")
                if len(parts) < 2:
                    return label
                
                label_part = parts[0][1:]  # Remove the leading '['
                # Encode brackets in the label part
                label_part_encoded = encode_brackets(label_part)
                # Reconstruct the markdown link with the encoded label
                encoded_label = f"[{label_part_encoded}]({parts[1]}"
                return encoded_label
                
        except Exception as e:
            # In case of any other unexpected error, log or print the error and return the original label
            print(f"Error processing label: {label}, error: {e}")
            return label

        # If none of the conditions above match, return the original label
        return label

    for column in columns:
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
    termInfo["Synonyms"] = []
    
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
            termInfo["Examples"] = images
            # add a query to `queries` list for listing all available images
            q = ListAllAvailableImages_to_schema(termInfo["Name"], {"short_form":vfbTerm.term.core.short_form})
            queries.append(q)

        # If the term has channel images but not anatomy channel images, create thumbnails from channel images.
        if vfbTerm.channel_image and len(vfbTerm.channel_image) > 0:
            images = {}
            for image in vfbTerm.channel_image:
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
                    
                    # Enhanced publication handling - handle multiple publications
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

def serialize_solr_output(results):
    # Serialize the sanitized dictionary to JSON
    json_string = json.dumps(results.docs[0], ensure_ascii=False)
    json_string = json_string.replace('\\', '')
    json_string = json_string.replace('"{', '{')
    json_string = json_string.replace('}"', '}')
    json_string = json_string.replace("\'", '-')
    return json_string 

def get_term_info(short_form: str, preview: bool = False):
    """
    Retrieves the term info for the given term short form.

    :param short_form: short form of the term
    :return: term info
    """
    parsed_object = None
    try:
        # Search for the term in the SOLR server
        results = vfb_solr.search('id:' + short_form)
        # Check if any results were returned
        parsed_object = term_info_parse_object(results, short_form)
        if parsed_object:
            term_info = fill_query_results(parsed_object)
            if not term_info:
                print("Failed to fill query preview results!")
                return parsed_object
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

def get_instances(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves available instances for the given class short form.
    :param short_form: short form of the class
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: results rows
    """

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
    query = f"""
    MATCH (i:Individual:has_image)-[:INSTANCEOF]->(p:Class {{ short_form: '{short_form}' }}),
          (i)<-[:depicts]-(:Individual)-[r:in_register_with]->(:Template)-[:depicts]->(templ:Template),
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
        "headers": {
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
        },
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
            for row in df.to_dict("records")
        ],
        "count": total_count
    }

    return formatted_results

def get_templates(limit: int = -1, return_dataframe: bool = False):
    """Get list of templates

    :param limit: maximum number of results to return (default -1, returns all results)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns list of dicts.
    :return: list of templates (id, label, tags, source (db) id, accession_in_source) + similarity score.
    :rtype: pandas.DataFrame or list of dicts

    """
    count_query = """MATCH (t:Template)<-[:depicts]-(tc:Template)-[r:in_register_with]->(tc:Template)
                RETURN COUNT(DISTINCT t) AS total_count"""

    count_results = vc.nc.commit_list([count_query])
    count_df = pd.DataFrame.from_records(get_dict_cursor()(count_results))
    total_count = count_df['total_count'][0] if not count_df.empty else 0

    # Define the main Cypher query
    query = f"""
    MATCH (t:Template)-[:INSTANCEOF]->(p:Class),
          (t)<-[:depicts]-(tc:Template)-[r:in_register_with]->(tc:Template),
          (t)-[:has_source]->(ds:DataSet)-[:has_license]->(lic:License)
    RETURN t.short_form as id,
           apoc.text.format("[%s](%s)",[COALESCE(t.symbol[0],t.label),t.short_form]) AS name,
           apoc.text.join(t.uniqueFacets, '|') AS tags,
           apoc.text.format("[%s](%s)",[COALESCE(ds.symbol[0],ds.label),ds.short_form]) AS dataset,
           REPLACE(apoc.text.format("[%s](%s)",[COALESCE(lic.symbol[0],lic.label),lic.short_form]), '[null](null)', '') AS license,
           REPLACE(apoc.text.format("[![%s](%s '%s')](%s)",[COALESCE(t.symbol[0],t.label), REPLACE(COALESCE(r.thumbnail[0],""),"thumbnailT.png","thumbnail.png"), COALESCE(t.symbol[0],t.label), t.short_form]), "[![null]( 'null')](null)", "") as thumbnail,
           99 as order
           ORDER BY id Desc
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
                for row in df.to_dict("records")
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
                for row in df.to_dict("records")
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
                for row in df.to_dict("records")
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
                for row in df.to_dict("records")
            ],
            "count": total_count
        }
    
    return results


def contains_all_tags(lst: List[str], tags: List[str]) -> bool:
    """
    Checks if the given list contains all the tags passed.

    :param lst: list of strings to check
    :param tags: list of strings to check for in lst
    :return: True if lst contains all tags, False otherwise
    """
    return all(tag in lst for tag in tags)

def fill_query_results(term_info):
    for query in term_info['Queries']:
        # print(f"Query Keys:{query.keys()}")
        
        if "preview" in query.keys() and (query['preview'] > 0 or query['count'] < 0) and query['count'] != 0:
            function = globals().get(query['function'])
            summary_mode = query.get('output_format', 'table') == 'ribbon'

            if function:
                # print(f"Function {query['function']} found")
                
                # Unpack the default dictionary and pass its contents as arguments
                function_args = query['takes'].get("default", {})
                # print(f"Function args: {function_args}")

                # Modify this line to use the correct arguments and pass the default arguments
                if summary_mode:
                    result = function(return_dataframe=False, limit=query['preview'], summary_mode=summary_mode, **function_args)
                else:
                    result = function(return_dataframe=False, limit=query['preview'], **function_args)
                # print(f"Function result: {result}")
                
                # Filter columns based on preview_columns
                filtered_result = []
                filtered_headers = {}
                
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
                elif isinstance(result, list) and all(isinstance(item, dict) for item in result):
                    for item in result:
                        if 'preview_columns' in query.keys() and len(query['preview_columns']) > 0:
                            filtered_item = {col: item[col] for col in query['preview_columns']}
                        else:
                            filtered_item = item
                        filtered_result.append(filtered_item)
                elif isinstance(result, pd.DataFrame):
                    filtered_result = result[query['preview_columns']].to_dict('records')
                else:
                    print(f"Unsupported result format for filtering columns in {query['function']}")
                
                query['preview_results'] = {'headers': filtered_headers, 'rows': filtered_result}
                query['count'] = result['count']
                # print(f"Filtered result: {filtered_result}")
            else:
                print(f"Function {query['function']} not found")
        else:
            print("Preview key not found or preview is 0")
    return term_info
