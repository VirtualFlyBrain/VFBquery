import re
import json
import requests
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List, Optional
from dacite import from_dict


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
			return get_link(self.label.replace("\\'", "'"), self.short_form) + " " + self.get_types_str(show_types)
		return get_link(self.short_form, self.short_form) + " " + self.get_types_str(show_types)

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


@dataclass_json
@dataclass
class Pub:
	core: MinimalEntityInfo
	microref: Optional[str] = ""
	PubMed: Optional[str] = ""
	FlyBase: Optional[str] = ""
	DOI: Optional[str] = ""
	ISBN: Optional[str] = ""

	def get_microref(self):
		if self.microref:
			return self.core.get_int_link().replace(self.core.label, self.microref)
		# if microref doesn't exist create one from the label:
		if self.core.label:
			if "," in self.core.label:
				label_parts = self.core.label.split(",")
				self.microref = label_parts[0] + "," + label_parts[1]
				return self.core.intLink().replace(self.core.label, self.microref);
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
		# CONTINUE
		pass


@dataclass_json
@dataclass
class Dataset:
	core: MinimalEntityInfo
	link: Optional[str] = ""
	icon: Optional[str] = ""

	def get_ext_link(self):
		if not self.core.label or self.core.label == "null":
			return ""
		# TODO link + src + label ???
		if self.icon:
			return get_link(self.core.label, self.link) + "(" + self.icon + ")"
		else:
			return get_link(self.core.label, self.link)

	# TODO double check the returned structure with Robbie
	def get_int_link(self):
		if not self.core.label or self.core.label == "null":
			return ""
		result = self.core.get_int_link(False)
		if self.icon:
			result += get_link(self.core.label, self.get_secure_url(self.icon))
		if self.link and self.link != "unspec":
			# TODO CONTINUE
			pass



	def get_secure_url(self, url):
		secure_url = url.replace("http://", "http://")
		if self.check_url_exist(secure_url):
			return secure_url
		return url

	def check_url_exist(self, url: str) -> bool:
		try:
			response = requests.get(url)
			if response.status_code == 200:
				return True
		except Exception as e:
			print("Error checking url (" + url + ") " + str(e))
		return False


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


@dataclass_json
@dataclass
class Image:
	image_folder: str
	index: List[float]
	template_channel: MinimalEntityInfo
	template_anatomy: MinimalEntityInfo


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


@dataclass_json
@dataclass
class ChannelImage:
	image: Image
	channel: MinimalEntityInfo
	imaging_technique: MinimalEntityInfo


@dataclass_json
@dataclass
class Domain:
	index: List[float]
	center: dict
	folder: str
	anatomical_individual: MinimalEntityInfo
	anatomical_type: MinimalEntityInfo


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
class Coordinates:
	X: float
	Y: float
	Z: float


@dataclass_json
@dataclass
class CoordinatesList:
	coordinates: List[float]


@dataclass_json
@dataclass
class CoordinatesJsonList:
	coordinates: List[str]


@dataclass_json
@dataclass
class CoordinatesJsonString:
	json: Coordinates


@dataclass_json
@dataclass
class AnatomyChannelImage:
	anatomy: MinimalEntityInfo
	channel_image: ChannelImage


@dataclass_json
@dataclass
class CoordinatesList:
	coordinates: list


@dataclass_json
@dataclass
class VfbTerminfo:
	term: Term
	query: str
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
		result = ""
		if self.dataset_license:
			for dsl in self.dataset_license:
				if self.term.core.short_form == dsl.dataset.core.short_form:
					if dsl.license.get_ext_link() not in result:
						result += dsl.license.get_ext_link()
					elif dsl.license.get_int_link() not in result:
						result += dsl.license.get_int_link()
		elif self.license:
			# CONTINUE
			pass
		return result

	def get_definition(self) -> str:
		if self.def_pubs:
			return self.term.get_definition() + "\n(" + self.get_minirefs(self.def_pubs, ", ") + ")"
		return self.term.get_definition()

	def get_minirefs(self, pubs: List[Pub], sep: str) -> str:
		return sep.join([pub.get_microref() for pub in pubs])

	def get_synonyms(self) -> str:
		if self.pub_syn:
			return ", ".join([str(syn) for syn in set(self.pub_syn) if syn])
		return ""


def get_link(text: str, link: str) -> str:
	"""
	Creates a markdown formatted link string.

	:param text: label of the link
	:param link: source url of the link
	:return: markdown formatted link string
	"""
	return "[{}]({})".format(text, link)


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


def serialize_term_info_to_dict(vfb_term: VfbTerminfo, show_types=False) -> dict:
	"""
	Serializes the given VfbTerminfo to a dictionary

	:param vfb_term: term info object
	:param show_types: show type detail in serialization
	:return: dictionary representation of the term info object
	"""
	data = dict()
	data["label"] = "{0} [{1}] {2}".format(vfb_term.term.core.label, vfb_term.term.core.short_form, vfb_term.term.core.get_types_str(show_types)).strip()

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

	return data


def serialize_term_info_to_json(vfb_term: VfbTerminfo, show_types=False) -> str:
	"""
	Serializes the given VfbTerminfo to a json string

	:param vfb_term: term info object
	:param show_types: show type detail in serialization
	:return: json string representation of the term info object
	"""
	term_info_dict = serialize_term_info_to_dict(vfb_term, show_types)
	return json.dumps(term_info_dict, indent=4)
