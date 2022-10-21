from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List, Optional


@dataclass_json
@dataclass
class MinimalEntityInfo:
	short_form: str = ""
	iri: str = ""
	label: str = ""
	types: List[str] = None
	unique_facets: List[str] = None
	symbol: str = ""


@dataclass_json
@dataclass
class MinimalEdgeInfo:
	short_form: str = ""
	iri: str = ""
	label: str = ""
	type: str = ""


@dataclass_json
@dataclass
class Synonym:
	label: str
	scope: str
	type: str


@dataclass_json
@dataclass
class PubSpecificContent:
	title: str = ""
	PubMed: str = ""
	FlyBase: str = ""
	DOI: str = ""
	ISBN: str = ""


@dataclass_json
@dataclass
class Pub:
	core: MinimalEntityInfo
	microref: str = ""
	PubMed: str = ""
	FlyBase: str = ""
	DOI: str = ""
	ISBN: str = ""


@dataclass_json
@dataclass
class PubSyn:
	synonym: Synonym = None
	pub: Optional[Pub] = None
	pubs: Optional[List[Pub]] = None


@dataclass_json
@dataclass
class License:
	core: MinimalEntityInfo
	link: str
	icon: str
	is_bespoke: bool


@dataclass_json
@dataclass
class Dataset:
	core: MinimalEntityInfo
	link: str
	icon: str


@dataclass_json
@dataclass
class DatasetLicense:
	dataset: Dataset
	license: License


@dataclass_json
@dataclass
class Xref:
	homepage: str
	link_base: str
	link_postfix: str
	accession: str
	link_text: str
	icon: str
	site: MinimalEntityInfo


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
	center: str
	extent: str
	voxel: str
	orientation: str
	image_folder: str
	channel: MinimalEntityInfo


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


def deserialize_term_info(terminfo: str) -> VfbTerminfo:
	"""
	Deserializes the given terminfo string to the object.
	:param terminfo: vfb_json string
	:return: VfbTerminfo object
	"""
	return VfbTerminfo.from_json(terminfo)

