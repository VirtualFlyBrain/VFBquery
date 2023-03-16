import re
import json
import requests
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List, Optional, Any
from dacite import from_dict


@dataclass_json
@dataclass
class Coordinates:
    X: float
    Y: float
    Z: float

    def __str__(self):
        return json.dumps([str(self.X), str(self.Y), str(self.Z)])


class CoordinatesFactory:

    @staticmethod
    def from_list(float_list: List[float]) -> Coordinates:
        return Coordinates(float_list[0], float_list[1], float_list[2])

    @staticmethod
    def from_json_string(json_str: str) -> Coordinates:
        return  Coordinates.from_json(json_str)

    @staticmethod
    def from_json_string_list(json_str_list: List[str]) -> Coordinates:
        return Coordinates.from_json(json_str_list[0])


@dataclass_json
@dataclass
class MinimalEntityInfo:
    short_form: Optional[str] = ""
    iri: Optional[str] = ""
    label: Optional[str] = ""
    types: Optional[List[str]] = None
    unique_facets: Optional[List[str]] = None
    symbol: Optional[str] = ""

    def get_int_link(self, show_types=False) -> str:
        if self.label:
            result = get_link(self.label.replace("\\'", "'"), self.short_form) + " " + self.get_types_str(show_types)
        else:
            result = get_link(self.short_form, self.short_form) + " " + self.get_types_str(show_types)
        return result.strip()

    def get_ext_link(self, show_types=False) -> str:
        return get_link(self.short_form, self.iri) + " " + self.get_types_str(show_types)

    def get_types_str(self, show_types: bool) -> str:
        if show_types and self.unique_facets:
            return " " + self.return_type(self.unique_facets)
        if show_types and self.types:
            return " " + self.return_type(self.types)
        return ""

    def return_type(self, type_list: List[str]) -> str:
        return " ".join([typ.replace("_", " ") for typ in type_list])


@dataclass_json
@dataclass
class MinimalEdgeInfo:
    short_form: Optional[str] = ""
    iri: Optional[str] = ""
    label: Optional[str] = ""
    type: Optional[str] = ""


@dataclass_json
@dataclass
class Synonym:
    label: Optional[str] = ""
    scope: Optional[str] = ""
    type: Optional[str] = ""

    def __str__(self):
        if self.scope:
            return re.sub(r"([^_A-Z])([A-Z])", r"\1 \2", self.scope).replace("has ", "") + ": " + self.label
        return self.label


@dataclass_json
@dataclass
class PubSpecificContent:
    title: Optional[str] = ""
    PubMed: Optional[str] = ""
    FlyBase: Optional[str] = ""
    DOI: Optional[str] = ""
    ISBN: Optional[str] = ""

    def get_refs(self):
        results = list()
        if self.FlyBase and len(self.FlyBase) > 2:
            results.append(self.FlyBase)
        if self.PubMed and len(self.PubMed) > 2:
            results.append(self.PubMed)
        if self.DOI and len(self.DOI) > 2:
            results.append(self.DOI)
        return results


@dataclass_json
@dataclass
class Pub:
    core: MinimalEntityInfo
    microref: Optional[str] = ""
    PubMed: Optional[str] = ""
    FlyBase: Optional[str] = ""
    DOI: Optional[str] = ""
    ISBN: Optional[str] = ""

    def get_miniref(self) -> Optional[dict]:
        links = list()
        if self.core.short_form == "Unattributed":
            return None
        site_links = dict()
        site_links["FlyBase"] = "http://flybase.org/reports/$ID"
        site_links["DOI"] = "https://doi.org/$ID"
        site_links["PubMed"] = "http://www.ncbi.nlm.nih.gov/pubmed/?term=$ID"

        result = self.core.get_int_link()
        if self.FlyBase:
            links.append(site_links["FlyBase"].replace("$ID", self.FlyBase))
        if self.DOI:
            links.append(site_links["DOI"].replace("$ID", self.DOI))
        if self.PubMed:
            links.append(site_links["PubMed"].replace("$ID", self.PubMed))

        return {"link": result, "refs": links, "types": self.core.get_types_str(True)}

    def get_microref(self) -> str:
        if self.microref:
            return self.core.get_int_link().replace(self.core.label, self.microref)
        # if microref doesn't exist create one from the label:
        if self.core.label:
            if "," in self.core.label:
                label_parts = self.core.label.split(",")
                self.microref = label_parts[0] + "," + label_parts[1]
                return self.core.get_int_link().replace(self.core.label, self.microref)
            else:
                return self.core.label
        return ""


@dataclass_json
@dataclass
class PubSyn:
    synonym: Synonym = None
    pub: Optional[Pub] = None
    pubs: Optional[List[Pub]] = None

    def __str__(self):
        if self.pub and self.pub.get_microref():
            return str(self.synonym) + " (" + self.pub.get_microref() + ")"
        if self.pubs:
            return str(self.synonym) + " " + self.get_microrefs()
        return str(self.synonym)

    def __hash__(self):
        return hash(self.__str__())

    def get_microrefs(self):
        return "(" + ", ".join([pub.get_microref() for pub in self.pubs]) + ")"


@dataclass_json
@dataclass
class License:
    core: MinimalEntityInfo
    link: Optional[str] = ""
    icon: Optional[str] = ""
    is_bespoke: Optional[str] = ""

    def get_ext_link(self):
        result = dict()
        if self.core.label:
            result["label"] = get_link(self.core.label, self.link)
        if self.icon:
            result["icon"] = self.icon
        return result

    def get_int_link(self):
        result = dict()
        if self.core.label:
            result["label"] = self.core.get_int_link()
        if self.icon:
            result["icon"] = self.icon
        return result


@dataclass_json
@dataclass
class Dataset:
    core: MinimalEntityInfo
    link: Optional[str] = ""
    icon: Optional[str] = ""

    def get_ext_link(self):
        if not self.core.label or self.core.label == "null":
            return ""
        result = dict()
        result["label"] = get_link(self.core.label, self.link)
        if self.icon:
            result["icon"] = self.get_secure_url(self.icon)
        return result

    def get_int_link(self):
        result = dict()
        if not self.core.label or self.core.label == "null":
            return ""
        result["label"] = self.core.get_int_link(False)
        if self.icon:
            result["icon"] = self.get_secure_url(self.icon)
        if self.link and self.link != "unspec":
            result["link"] = self.link
        return result


@dataclass_json
@dataclass
class DatasetLicense:
    dataset: Dataset
    license: License


@dataclass_json
@dataclass
class Xref:
    site: MinimalEntityInfo
    homepage: Optional[str] = ""
    link_base: Optional[str] = ""
    link_postfix: Optional[str] = ""
    accession: Optional[str] = ""
    link_text: Optional[str] = ""
    icon: Optional[str] = ""

    def get_ext_link(self, show_types: bool = False):
        result = dict()
        result["label"] = get_link(self.link_text, self.link())
        result["site"] = self.site.get_ext_link(show_types).replace(self.site.iri, self.link())
        if self.icon:
            result["icon"] = get_secure_url(self.icon, False, timeout=5)
        return result

    def link(self):
        if self.accession and self.accession != "None":
            return self.link_base + self.accession + self.link_postfix
        if self.homepage:
            return self.homepage
        return self.site.iri


@dataclass_json
@dataclass
class Image:
    index: List[float]
    template_channel: MinimalEntityInfo
    template_anatomy: MinimalEntityInfo
    image_folder: str
    image_nrrd: Optional[str] = ""
    image_obj: Optional[str] = ""
    image_thumbnail: Optional[str] = ""
    image_wlz: Optional[str] = ""
    image_swc: Optional[str] = ""

@dataclass_json
@dataclass
class TemplateChannel:
    index: List[float]
    channel: MinimalEntityInfo
    center: Optional[str] = ""
    extent: Optional[str] = ""
    voxel: Optional[str] = ""
    orientation: Optional[str] = ""
    image_folder: Optional[str] = ""
    image_nrrd: Optional[str] = ""
    image_obj: Optional[str] = ""
    image_thumbnail: Optional[str] = ""
    image_wlz: Optional[str] = ""
    image_swc: Optional[str] = ""

    def get_voxel(self) -> Coordinates:
        return CoordinatesFactory.from_json_string(self.voxel)

    def get_center(self) -> Coordinates:
        return CoordinatesFactory.from_json_string(self.center)

    def get_extent(self) -> Coordinates:
        return CoordinatesFactory.from_json_string(self.extent)


@dataclass_json
@dataclass
class ChannelImage:
    image: Image
    channel: MinimalEntityInfo
    imaging_technique: MinimalEntityInfo

    def get_url(self, pre: str, post: str) -> str:
        try:
            if self.image and pre == "" and ("volume" in post or post == "thumbnailT.png" or post == "citations.bibtex"):
                if ".obj" in post:
                    return self.image.image_obj.replace("http://", "https://")
                if ".swc" in post:
                    return self.image.image_swc.replace("http://", "https://")
                if "thumbnail.png" in post:
                    return self.image.image_thumbnail.replace("http://", "https://").replace("thumbnailT.png","thumbnail.png")
                if "thumbnailT.png" in post:
                    return self.image.image_thumbnail.replace("http://", "https://").replace("thumbnail.png","thumbnailT.png")
                if ".nrrd" in post:
                     return self.image.image_nrrd.replace("http://", "https://")
                if ".wlz" in post:
                     return self.image.image_wlz.replace("http://", "https://")
                if ".bibtex" in post:
                     return (self.image.image_folder + post).replace("http://", "https://")
        except Exception as e:
            print("Error in ChannelImage.get_url() " + str(e))

        return ""


@dataclass_json
@dataclass
class Domain:
    index: List[float]
    center: Any
    folder: str
    anatomical_individual: MinimalEntityInfo
    anatomical_type: MinimalEntityInfo
    image_nrrd: Optional[str] = ""
    image_obj: Optional[str] = ""
    image_thumbnail: Optional[str] = ""
    image_wlz: Optional[str] = ""
    image_swc: Optional[str] = ""

    def get_center(self) -> Optional[Coordinates]:
        if isinstance(self.center, str):
            return CoordinatesFactory.from_json_string(str(self.center))
        return None


@dataclass_json
@dataclass
class AnatomyChannelImage:
    anatomy: MinimalEntityInfo
    channel_image: ChannelImage


@dataclass_json
@dataclass
class Rel:
    relation: MinimalEdgeInfo
    object: MinimalEntityInfo

    def get_int_link(self, show_types: bool = False):
        return self.relation.label + " " + self.object.get_int_link(show_types)


@dataclass_json
@dataclass
class Term:
    core: MinimalEntityInfo
    description: List[str]
    comment: List[str]
    iri: str = ""
    link: str = ""
    icon: str = ""

    def get_definition(self):
        result = ""
        if self.description:
            result += self.get_description()
        if self.comment:
            result = result + " \n " + self.get_comment()
        return result.strip()

    def get_description(self):
        if self.description:
            return self.encode("\n".join(self.description))
        return ""

    def get_comment(self):
        if self.comment:
            return self.encode("\n".join(self.comment))
        return ""

    def encode(self, text):
        return text.replace("\\\"", "\"").replace("\\\'", "\'")

    def get_logo(self):
        result = ""
        if self.icon:
            if self.link:
                result = get_link(self.link, self.icon)
            else:
                result = self.icon
        return result

    def get_link(self):
        result = ""
        if self.link:
            result = get_link(self.link, self.link)
        return result


@dataclass_json
@dataclass
class AnatomyChannelImage:
    anatomy: MinimalEntityInfo
    channel_image: ChannelImage

    def get_url(self, pre: str, post: str):
        return self.channel_image.get_url(pre, post)


@dataclass_json
@dataclass
class CoordinatesList:
    coordinates: list


@dataclass_json
@dataclass
class VfbTerminfo:
    term: Term
    query: Optional[str]
    version: str
    anatomy_channel_image: Optional[List[AnatomyChannelImage]] = None
    xrefs: Optional[List[Xref]] = None
    pub_syn: Optional[List[PubSyn]] = None
    def_pubs: Optional[List[Pub]] = None
    pubs: Optional[List[Pub]] = None
    pub: Optional[Pub] = None
    license: Optional[List[License]] = None
    dataset_license: Optional[List[DatasetLicense]] = None
    relationships: Optional[List[Rel]] = None
    related_individuals: Optional[List[Rel]] = None
    parents: Optional[List[MinimalEntityInfo]] = None
    channel_image: Optional[List[ChannelImage]] = None
    template_domains: Optional[List[Domain]] = None
    template_channel: Optional[TemplateChannel] = None
    targeting_splits: Optional[List[MinimalEntityInfo]] = None
    target_neurons: Optional[List[MinimalEntityInfo]] = None
    pub_specific_content: Optional[PubSpecificContent] = None

    def get_source(self):
        result = ""
        if self.dataset_license:
            for dsl in self.dataset_license:
                if self.term.core.short_form == dsl.dataset.core.short_form:
                    if dsl.dataset.get_ext_link() not in result:
                        result += dsl.dataset.get_ext_link()
                    else:
                        result += dsl.dataset.get_int_link()
        return result

    def get_license(self):
        result = list()
        if self.dataset_license:
            for dsl in self.dataset_license:
                if self.term.core.short_form == dsl.dataset.core.short_form:
                    if dsl.license.get_ext_link() and dsl.license.get_ext_link() not in result:
                        result.append(dsl.license.get_ext_link())
                elif dsl.license.get_int_link() and dsl.license.get_int_link() not in result:
                    result.append(dsl.license.get_int_link())
        elif self.license:
            for lcns in self.license:
                if self.term.core.short_form == lcns.core.short_form:
                    if lcns.get_ext_link() and lcns.get_ext_link() not in result:
                        result.append(lcns.get_ext_link())
                elif lcns.get_int_link() and lcns.get_int_link() not in result:
                    result.append(lcns.get_int_link())

        return result

    def get_domains(self) -> List[List[str]]:
        domains = list()
        try:
            if "Template" in self.term.core.types and self.template_channel and self.template_domains:
                wlzUrl = ""
                domain_id = [""] * 600
                domain_name = [""] * 600
                domain_type = [""] * 600
                domain_centre = [""] * 600
                voxel_size = [""] * 4
                domain_id[0] = self.term.core.short_form
                domain_name[0] = self.parents[0].label
                domain_type[0] = self.parents[0].short_form
                voxel_size[0] = str(self.template_channel.get_voxel().get_x())
                voxel_size[1] = str(self.template_channel.get_voxel().get_y())
                voxel_size[2] = str(self.template_channel.get_voxel().get_z())
                domain_centre[0] = str(self.template_channel.get_center())
                for domain in self.template_domains:
                    if domain.index:
                        domain_id[int(domain.index[0])] = domain.anatomical_individual.short_form
                        domain_name[int(domain.index[0])] = domain.anatomical_type.label
                        domain_type[int(domain.index[0])] = domain.anatomical_type.short_form
                        if domain.get_center() and domain.get_center().Z:
                            domain_centre[int(domain.index[0])] = str(domain.get_center())
                domains.append(voxel_size)
                domains.append(domain_id)
                domains.append(domain_name)
                domains.append(domain_type)
                domains.append(domain_centre)
            else:
                domains.append(["0.622088", "0.622088", "0.622088", ""])
                domains.append([self.term.core.short_form])
                domains.append([self.term.core.label])
                domains.append([self.term.core.short_form])
                domains.append(["[511, 255, 108]"])
        except Exception as e:
            print("Error in vfbTerm.get_domains() " + str(e))

        return domains

    def get_definition(self) -> str:
        if self.def_pubs:
            return self.term.get_definition() + "\n(" + self.get_minirefs(self.def_pubs, ", ") + ")"
        return self.term.get_definition()

    def get_targeting_splits(self) -> List[str]:
        results = set()
        if self.targeting_splits:
            for split in self.targeting_splits:
                results.add(split.get_int_link())
        return list(results)

    def get_targeting_neurons(self) -> List[str]:
        results = set()
        if self.target_neurons:
            for neuron in self.target_neurons:
                results.add(neuron.get_int_link())
        return list(results)

    @staticmethod
    def get_minirefs(pubs: List[Pub], sep: str) -> str:
        return sep.join([pub.get_microref() for pub in pubs])

    def get_synonyms(self) -> List[str]:
        if self.pub_syn:
            return [str(syn) for syn in set(self.pub_syn) if syn]
        return list()

    def get_references(self) -> List[dict]:
        results = list()
        if self.def_pubs:
            for pub in self.def_pubs:
                mini_ref = pub.get_miniref()
                if mini_ref and mini_ref not in results:
                    results.append(mini_ref)
        if self.pub_syn:
            for syn in self.pub_syn:
                mini_ref = syn.pub.get_miniref()
                if mini_ref and mini_ref not in results:
                    results.append(mini_ref)
        if self.pubs:
            for pub in self.pubs:
                mini_ref = pub.get_miniref()
                if mini_ref and mini_ref not in results:
                    results.append(mini_ref)
        return results

    @staticmethod
    def get_rel_list(entities: List[Rel], show_types: bool) -> List[str]:
        values = list()
        for rel in entities:
            if rel.get_int_link(show_types) not in values:
                values.append(rel.get_int_link(show_types))
        return values

    @staticmethod
    def compile_list(entities: List[MinimalEntityInfo], show_types: bool) -> List[str]:
        values = list()
        for entity in entities:
            if entity.get_int_link(show_types) not in values:
                values.append(entity.get_int_link(show_types))
        return values

    def get_xref_list(self):
        results = list()
        if self.xrefs:
            for xref in self.xrefs:
                results.append(xref.get_ext_link())
            # sort xrefs alphabetically (by site)
            results = sorted(results, key=lambda d: d['label'])

        if self.pub_specific_content:
            for ref in self.pub_specific_content.get_refs():
                results.append(ref)

        return results

    def get_thumbnails(self, template: str) -> Optional[List[dict]]:
        image_array = list()
        try:
            if not template:
                # default to JFRC2
                template = "VFB_00017894"
            for ci in self.channel_image:
                # add same template to the beginning and others at the end.
                if ci and ci.image and ci.image.template_anatomy and ci.image.template_anatomy.short_form \
                        and template == ci.image.template_anatomy.short_form:
                    image_array.append(self.get_image(ci.get_url("", "thumbnailT.png"), self.term.core.label, self.term.core.short_form))
            for ci in self.channel_image:
                # add same template to the beginning and others at the end.
                if ci and ci.image and ci.image.template_anatomy and ci.image.template_anatomy.short_form \
                        and template != ci.image.template_anatomy.short_form:
                    image_array.append(self.get_image(ci.get_url("", "thumbnailT.png"),
                                                      self.term.core.label + " [" + ci.image.template_anatomy.label + "]",
                                                      "[" + ci.image.template_anatomy.short_form + "," + self.term.core.short_form + "]"))
        except Exception as e:
            print("Error in vfbTerm.get_thumbnails(): " + str(e))
            return None
        return image_array

    def get_examples(self, template: str) -> Optional[List[dict]]:
        image_array = list()
        try:
            if not template:
                # default to JRC2018Unisex
                template = "VFB_00101567"
            for anat in self.anatomy_channel_image:
                # add same template to the beginning and others at the end.
                if anat.channel_image and anat.channel_image.image and anat.channel_image.image.template_anatomy \
                        and anat.channel_image.image.template_anatomy.short_form \
                        and template == anat.channel_image.image.template_anatomy.short_form:
                    image_array.append(self.get_image(anat.get_url("", "thumbnailT.png"), anat.anatomy.label, anat.anatomy.short_form))
            for anat in self.anatomy_channel_image:
                # add same template to the beginning and others at the end.
                if anat.channel_image and anat.channel_image.image and anat.channel_image.image.template_anatomy \
                        and anat.channel_image.image.template_anatomy.short_form \
                        and template != anat.channel_image.image.template_anatomy.short_form:
                    image_array.append(self.get_image(anat.get_url("", "thumbnailT.png"), anat.anatomy.label, anat.anatomy.short_form))
        except Exception as e:
            print("Error in vfbTerm.get_examples(): " + str(e))
            return None
        return image_array

    def get_thumbnail(self):
        image_array = list()
        try:
            thumbnail = self.template_channel.image_thumbnail
            if "png" in thumbnail:
                thumbnail = thumbnail.replace("thumbnail.png","thumbnailT.png") # swap to transparent version
            else:
                thumbnail = self.template_channel.image_folder + "thumbnailT.png"
            image_array.append(self.get_image(thumbnail, self.term.core.label, self.term.core.short_form))
        except Exception as e:
            print("Error in vfbTerm.get_thumbnail(): " + str(e))
            return None
        return image_array

    def get_cluster_image(self):
        image_array = list()
        try:
            image_array.append(self.get_image(self.xrefs[0].link_base + self.xrefs[0].accession + "/snapshot.png",
                                              self.term.core.label, self.term.core.short_form))
        except Exception as e:
            print("Error in vfbTerm.get_cluster_image(): " + str(e))
            return None
        return image_array

    @staticmethod
    def get_image_file(images: List[ChannelImage], file_name: str) -> str:
        try:
            for ci in images:
                if check_url_exist(ci.get_url("", file_name), allow_redirects=False):
                    return ci.get_url("", file_name)
        except Exception as e:
            print("Failed to find: " + file_name)
            print(e)
        return ""

    @staticmethod
    def get_image_file2(ci: ChannelImage, file_name: str) -> str:
        try:
            return ci.get_url("", file_name)
        except Exception as e:
            print("Failed to find: " + file_name)
            print(e)
        return ""

    @staticmethod
    def get_image_file3(template: TemplateChannel, file_name: str) -> str:
        try:
            if check_url_exist(template.image_folder + file_name, allow_redirects=False):
                return template.image_folder + file_name
        except Exception as e:
            print("Failed to find: " + file_name)
            print(e)
        return ""

    @staticmethod
    def get_image(data: str, name: str, reference: str):
        image = dict()
        image["name"] = name
        image["data"] = get_secure_url(data)
        image["reference"] = reference
        image["format"] = "PNG"
        return image


def get_link(text: str, link: str) -> str:
    """
    Creates a markdown formatted link string.

    :param text: label of the link
    :param link: source url of the link
    :return: markdown formatted link string
    """
    return "[{}]({})".format(text, link)


def get_secure_url(url: str, allow_redirects: bool = True, timeout=15) -> str:
    secure_url = url.replace("http://", "http://")
    if check_url_exist(secure_url, allow_redirects, timeout):
        return secure_url
    return url


def check_url_exist(url: str, allow_redirects: bool = False, timeout=15, request_method: str = "HEAD") -> bool:
    if ":" in url:
        try:
            if request_method == "GET":
                response = requests.get(url, allow_redirects=allow_redirects, timeout=timeout)
            else:
                response = requests.head(url, allow_redirects=allow_redirects, timeout=timeout)
            if response.status_code == 200:
                return True
        except Exception as e:
            print("Error checking url (" + url + ") " + str(e))
    return False


def deserialize_term_info(terminfo: str) -> VfbTerminfo:
    """
    Deserializes the given terminfo vfb_json string to VfbTerminfo object.

    :param terminfo: vfb_json string
    :return: VfbTerminfo object
    """
    return VfbTerminfo.from_json(terminfo)


def deserialize_term_info_from_dict(terminfo: dict) -> VfbTerminfo:
    """
    Deserializes the given terminfo vfb_json dictionary to VfbTerminfo object.

    :param terminfo: vfb_json dictionary
    :return: VfbTerminfo object
    """
    return from_dict(data_class=VfbTerminfo, data=terminfo)


def serialize_term_info_to_dict(vfb_term: VfbTerminfo, variable, loaded_template: Optional[str] = None, show_types=False) -> dict:
    """
    Serializes the given VfbTerminfo to a dictionary.

    :param vfb_term: term info object
    :param variable:
    :param loaded_template: template loaded to the geppetto
    :param show_types: show type detail in serialization
    :return: dictionary representation of the term info object
    """
    template = ""
    if loaded_template:
        template = loaded_template
    else:
        loaded_template = "VFB_00101567"

    data = dict()
    data["label"] = "{0} [{1}] {2}".format(vfb_term.term.core.label, vfb_term.term.core.short_form, vfb_term.term.core.get_types_str(show_types)).strip()

    class_variable = dict()
    if vfb_term.pub_specific_content and vfb_term.pub_specific_content.title:
        data["title"] = vfb_term.pub_specific_content.title

    if vfb_term.term.core.symbol:
        data["symbol"] = vfb_term.term.core.symbol

    if vfb_term.term.get_logo():
        data["logo"] = vfb_term.term.get_logo()

    if vfb_term.term.get_link():
        data["link"] = vfb_term.term.get_link()

    data["types"] = vfb_term.term.core.types

    if vfb_term.get_definition():
        data["description"] = vfb_term.get_definition()

    if vfb_term.get_synonyms():
        data["synonyms"] = vfb_term.get_synonyms()

    if vfb_term.get_source():
        data["source"] = vfb_term.get_source()

    if vfb_term.get_license() and not vfb_term.pub_specific_content:
        data["license"] = vfb_term.get_license()

    if vfb_term.parents:
        data["Classification"] = vfb_term.compile_list(vfb_term.parents, show_types)
        class_variable["id"] = vfb_term.parents[0].short_form
        class_variable["name"] = vfb_term.parents[0].label

    if vfb_term.relationships:
        data["relationships"] = vfb_term.get_rel_list(vfb_term.relationships, show_types)

    if vfb_term.related_individuals:
        data["related_individuals"] = vfb_term.get_rel_list(vfb_term.related_individuals, show_types)

    if vfb_term.xrefs or vfb_term.pub_specific_content:
        data["xrefs"] = vfb_term.get_xref_list()

    download_files = list()
    download_data = list()

    # TODO this needs serious debugging
    if vfb_term.channel_image:
        old_template = template
        temp_link = ""
        count = 0

        data["downloads"] = dict()
        data["filemeta"] = dict()
        for alignment in vfb_term.channel_image:
            count += 1
            old_template = template
            template = alignment.image.template_anatomy.short_form
            download_files = list()
            # TODO seems only the last channel_image is processed, see count
            data["downloads_label"] = alignment.image.template_anatomy.label

            if loaded_template and loaded_template != template:
                if old_template:
                    template = old_template
                if not temp_link:
                    temp_link = alignment.image.template_anatomy.get_int_link()
                if len(vfb_term.channel_image) == count:
                    # Add OBJ only so the template detection is triggered

                    # OBJ - 3D mesh
                    temp_data = vfb_term.get_image_file2(alignment, "volume_man.obj")
                    if "obj" in temp_data:
                        if "_man" in temp_data:
                            download_files.append(get_link(variable.getId() + "_mesh.obj", get_secure_data_url(temp_data)))
                            download_data.append({"obj": {"url": get_secure_data_v2_url(temp_data), "local": template + "/MeshFiles(OBJ)/"}})
                        else:
                            download_files.append(get_link(variable.getId() + "_pointCloud.obj", get_secure_data_url(temp_data)))
                            download_data.append({"obj": {"url": get_secure_data_v2_url(temp_data), "local": template + "/PointCloudFiles(OBJ)/"}})

                    # Download - NRRD stack
                    temp_data = vfb_term.get_image_file2(alignment, "volume.nrrd")
                    if "nrrd" in temp_data:
                        download_files.append(get_link(variable.getId() + ".nrrd", get_secure_data_url(temp_data)))
                        download_data.append({"nrrd": {"url": get_secure_data_v2_url(temp_data), "local": template + "/SignalFiles(NRRD)/"}})
                        bibtex_local = template + "/RequiredCitations(BIBTEX)/" + variable.getId() + "_(" + variable.getName().replace(" ", "_") + ").bibtex"
                        download_files.append(get_link(variable.getId() + ".bibtex", get_secure_data_url(temp_data)))
                        download_data.append({"bibtex": {"url": get_secure_data_v2_url(temp_data), "local": bibtex_local}})
                        data["downloads"] = download_files
                        data["filemeta"] = download_data
            else:
                old_template = template
                if loaded_template:
                    loaded_template = template
                temp_link = alignment.image.template_anatomy.get_int_link()
                # OBJ - 3D mesh
                temp_data = vfb_term.get_image_file2(alignment, "volume_man.obj")
                if "obj" in temp_data:
                    if "_man" in temp_data:
                        download_files.append(get_link(variable.getId() + "_mesh.obj", get_secure_data_url(temp_data)))
                        download_data.append(
                            {"obj": {"url": get_secure_data_v2_url(temp_data), "local": template + "/MeshFiles(OBJ)/"}})
                    else:
                        download_files.append(get_link(variable.getId() + "_pointCloud.obj", get_secure_data_url(temp_data)))
                        download_data.append(
                            {"obj": {"url": get_secure_data_v2_url(temp_data), "local": template + "/PointCloudFiles(OBJ)/"}})

                # SWC - 3D mesh
                temp_data = vfb_term.get_image_file2(alignment, "volume.swc")
                if "swc" in temp_data:
                    download_files.append(get_link(variable.getId() + ".swc", get_secure_data_url(temp_data)))
                    download_data.append(
                        {"swc": {"url": get_secure_data_v2_url(temp_data), "local": template + "/MeshFiles(OBJ)/"}})

                # Slices - 3D slice viewer
                temp_data = vfb_term.get_image_file2(alignment, "volume.wlz")
                if "wlz" in temp_data:
                    download_files.append(get_link(variable.getId() + ".wlz", get_secure_data_url(temp_data)))
                    download_data.append(
                        {"wlz": {"url": get_secure_data_v2_url(temp_data), "local": template + "/Slices(WOOLZ)/"}})

                # Download - NRRD stack
                temp_data = vfb_term.get_image_file2(alignment, "volume.nrrd")
                if "nrrd" in temp_data:
                    download_files.append(get_link(variable.getId() + ".nrrd", get_secure_data_url(temp_data)))
                    download_data.append(
                        {"nrrd": {"url": get_secure_data_v2_url(temp_data), "local": template + "/SignalFiles(NRRD)/"}})
                    temp_data = vfb_term.get_image_file2(alignment, "citations.bibtex")
                    if temp_data:
                        download_files.append(get_link(variable.getId() + ".bibtex", get_secure_data_url(temp_data)))
                        download_data.append({"bibtex": {"url": get_secure_data_v2_url(temp_data),
                                                         "local": template + "/RequiredCitations(BIBTEX)/"}})
                    data["downloads"] = download_files
                    data["filemeta"] = download_data
                # throwing count out to prevent other OBJ loading
                count = 1000
        if template:
            data["template"] = temp_link
            if vfb_term.get_thumbnails(template):
                data["thumbnail"] = vfb_term.get_thumbnails(template)

    if vfb_term.template_channel and vfb_term.template_channel.image_folder:
        if template != "":
            template = variable.getId()
        data["template"] = vfb_term.term.core.get_int_link()
        data["thumbnail"] = vfb_term.get_thumbnail()
        # OBJ - 3D mesh
        temp_data = vfb_term.template_channel.image_obj.replace("http://","https://")
        if "obj" in temp_data:
            if "_man" in temp_data:
                download_files.append(get_link(variable.getId() + "_mesh.obj", get_secure_data_url(temp_data)))
                download_data.append({"obj": {"url": get_secure_data_v2_url(temp_data),
                                  "local": template + "/MeshFiles(OBJ)/" + variable.getId() + "_(" + variable.getName().replace(" ","_") + ").obj"}})
            else:
                download_files.append(get_link(variable.getId() + "_pointCloud.obj", get_secure_data_url(temp_data)))
                download_data.append({"obj": {"url": get_secure_data_v2_url(temp_data), "local": template + "/PointCloudFiles(OBJ)/" + variable.getId() + "_(" + variable.getName().replace(" ","_") + ").obj"}})

        # Slices - 3D slice viewer
        temp_data = vfb_term.template_channel.image_wlz
        if "wlz" in temp_data:
            download_files.append(get_link(variable.getId() + ".wlz", get_secure_data_url(temp_data)))
            download_data.append({"wlz": {"url": get_secure_data_v2_url(temp_data), "local": template + "/Slices(WOOLZ)/" + variable.getId() + "_(" + variable.getName().replace(" ", "_") + ").wlz"}})

        # Download - NRRD stack
        temp_data = vfb_term.template_channel.image_nrrd
        if "nrrd" in temp_data:
            download_files.append(get_link(variable.getId() + ".nrrd", get_secure_data_url(temp_data)))
            data["downloads"] = download_files
            download_data.append({"nrrd": {"url": get_secure_data_v2_url(temp_data), "local": template + "/SignalFiles(NRRD)/" + variable.getId() + "_(" + variable.getName().replace(" ","_") + ").nrrd"}})
            data["filemeta"] = download_data

    # examples
    if vfb_term.anatomy_channel_image and vfb_term.get_examples(template):
        data["examples"] = vfb_term.get_examples(template)

    # NBLAST Cluster
    if vfb_term.xrefs and "flybrain.mrc-lmb.cam.ac.uk/vfb/fc/clusterv/3" in vfb_term.xrefs[0].link_base:
        data["thumbnail"] = vfb_term.get_cluster_image()

    if vfb_term.get_references():
        data["references"] = vfb_term.get_references()

    # queries
    # TODO requires geppettoModelAccess.getQueries() ??

    # Targeting Splits
    temp_data = vfb_term.get_targeting_splits()
    if temp_data:
        data["targetingSplits"] = temp_data

    # Targeting Neurons
    temp_data = vfb_term.get_targeting_neurons()
    if temp_data:
        data["targetingNeurons"] = temp_data

    return data


def get_secure_data_url(data_url: str) -> str:
    """
    Generates a secure data url from the given url
    :param data_url: data url to secure
    :return: secured url
    """
    return data_url.replace("http://", "https://").replace("https://www.virtualflybrain.org/data/", "/data/")


def get_secure_data_v2_url(data_url: str) -> str:
    """
    Generates a secure data v2 url from the given url
    :param data_url: data url to secure
    :return: secured v2 url
    """
    return data_url.replace("http://", "https://").replace("https://www.virtualflybrain.org/data/",
                                                           "https://v2.virtualflybrain.org/data/")


def serialize_term_info_to_json(vfb_term: VfbTerminfo, show_types=False) -> str:
    """
    Serializes the given VfbTerminfo to a json string

    :param vfb_term: term info object
    :param show_types: show type detail in serialization
    :return: json string representation of the term info object
    """
    term_info_dict = serialize_term_info_to_dict(vfb_term, show_types)
    return json.dumps(term_info_dict, indent=4)


def process(term_info_response: dict, variable, loaded_template: Optional[str] = None, show_types=False) -> dict:
    """
    Processes the term info api response and generates its flat representation.
    :param term_info_response: TermInfo dict responded by the VFBConnect API
    :param variable: ?? TODO ask Robbie
    :param loaded_template: template loaded to the geppetto
    :param show_types: Switch to display types. Default: False
    :return: flat representation of the term info
    """
    term_info = deserialize_term_info_from_dict(term_info_response)
    return serialize_term_info_to_dict(term_info, variable, loaded_template, show_types)

