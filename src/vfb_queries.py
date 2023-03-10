import pysolr
from term_info_queries import deserialize_term_info
from vfb_connect.cross_server_tools import VfbConnect
from marshmallow import Schema, fields

# Connect to the VFB SOLR server
vfb_solr = pysolr.Solr('http://solr.virtualflybrain.org/solr/vfb_json/', always_commit=False, timeout=990)

# Create a VFB connection object for retrieving instances
vc = VfbConnect()

class Query:
  def __init__(self, query, label, function, takes, default):
    self.Query = query
    self.Label = label 
    self.Function = function 
    self.Takes = takes 
    self.Default = default 

class Image:
  def __init__(self, id, label, thumbnail, thumbnail_transparent):
    self.Id = id
    self.Label = label 
    self.Thumbnail = thumbnail 
    self.ThumbnailTransparent = thumbnail_transparent 

class ImageField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return value
        return {"Id": value.Id
                , "Label": value.Label
                , "Thumbnail": value.Thumbnail
                , "ThumbnailTransparent": value.ThumbnailTransparent
                }

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return value
        return Query(Id=value["Id"]
                     , Label=value["Label"]
                     , Thumbnail=value["Thumbnail"]
                     , ThumbnailTransparent=value["ThumbnailTransparent"])
    
class QueryField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return value
        return {"Query": value.Query
                , "Label": value.Label
                , "Function": value.Function
                , "Takes": value.Takes
                , "Default": value.Default
                }

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return value
        return Query(Query=value["Query"]
                     , Label=value["Label"]
                     , Function=value["Function"]
                     , Takes=value["Takes"]
                     , Default=value["Default"])

class TermInfoOutputSchemma(Schema):
    Name = fields.String(missing="")
    SuperTypes = fields.List(fields.String(), missing=[])
    Meta = fields.Dict(missing={})
    Tags = fields.List(fields.String(), missing=[])
    Description = fields.String(missing="")
    Comment = fields.List(fields.String(), missing=[])
    Queries = fields.List(QueryField(), missing=[])
    Images = fields.List(ImageField(), missing=[])
    IsTemplate = fields.Bool(missing=False)
    IsClass = fields.Bool(missing=False)
    IsIndividual = fields.Bool(missing=False)

def term_info_parse_object(results, short_form):
    termInfo = {}
    if results.hits > 0 and results.docs and len(results.docs) > 0:
        # Deserialize the term info from the first result
        vfbTerm = deserialize_term_info(results.docs[0]['term_info'][0])
        queries = []
        termInfo["Name"] = "[%s](%s)"%(vfbTerm.term.core.label, vfbTerm.term.core.short_form)
        termInfo["SuperTypes"] = vfbTerm.term.core.types
        try:
            # Retrieve tags from the term's unique_facets attribute
            termInfo["Tags"] = vfbTerm.term.core.unique_facets
        except NameError:
            # If unique_facets attribute doesn't exist, use the term's types
            termInfo["Tags"] = vfbTerm.term.core.types
        try:
            # Retrieve description from the term's description attribute
            termInfo["Description"] = "%s"%("".join(vfbTerm.term.description))
        except NameError:
            pass
        try:
            # Retrieve comment from the term's comment attribute
            termInfo["Comment"] = "%s"%("".join(vfbTerm.term.comment))
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
            queries.append({"query":"ListAllAvailableImages",label:"List all available images of %s"%(vfbTerm.term.core.label),"function":"get_instances","takes":[{"short_form":{"&&":["Class","Anatomy"]},"default":"%s"%(vfbTerm.term.core.short_form)}]})
            
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
              if not record["index"] in images.keys():
                  images[record["index"]]=[]
              record["thumbnail"] = image.folder.replace("http://","https://") + "thumbnail.png"
              record["thumbnail_transparent"] = image.folder.replace("http://","https://") + "thumbnailT.png"
              for key in vars(image).keys():
                  if "image_" in key and not ("thumbnail" in key or "folder" in key) and len(vars(image)[key]) > 1:
                      record[key.replace("image_","")] = vars(image)[key].replace("http://","https://")
              record["center"] = image.get_center()
              images[record["index"]].append(record)
                
            # Add the thumbnails to the term info
            termInfo["Domains"] = images

        # Add the queries to the term info
        termInfo["Queries"] = queries
 
    return TermInfoOutputSchemma().load({"term_info": termInfo})

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
