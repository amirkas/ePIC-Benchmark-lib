from pydantic import (
    BaseModel, Field, PlainSerializer, RootModel, ConfigDict,
    SerializeAsAny
)
from typing import (
    Literal, Dict, Optional, Union, ClassVar, Annotated, Any,
    Generic, TypeVar, Sequence, Tuple
)
from ePIC_benchmarks.detector.xpath import DetectorConfigXpath

OptionalString = Optional[str]
OptionalBool = Optional[bool]

AnnotatedOptionalString = Annotated[
    OptionalString,
    Field(default=None)
]
AnnotatedAttributeValue = Annotated[
    Union[None, int, float, str, bool],
    Field(default=None)
]
AnnotatedOptionalInt = Annotated[
    Union[None, int],
    Field(default=None),
    PlainSerializer(lambda x : str(x), return_type=str, when_used='always')
]
AnnotatedOptionalNum = Annotated[
    Union[None, int, float],
    Field(default=None),
    PlainSerializer(lambda x : str(x), return_type=str, when_used='always')
]

def serialize_xml_bools(val : OptionalBool) -> OptionalString:

    if val is None:
        return None
    elif val:
        return "true"
    else:
        return "false"

AnnotatedOptionalBool = Annotated[
    OptionalBool,
    Field(default=None),
    PlainSerializer(
        serialize_xml_bools, return_type=Optional[str], when_used='always'
    )
]

class XmlElement(BaseModel):

    element_tag : Literal[''] = Field(default='', init=False)
    update_attribute : Optional[Literal['']] = None
    update_type : Optional[Literal['SET', 'ADD', 'DELETE']] = None
    update_value : AnnotatedAttributeValue

    def create_queries(self) -> Sequence[str]:

        all_queries = []
        self._query_helper([''], all_queries)
        return all_queries

    def _query_helper(self, parent_queries : Sequence[str], all_queries : Sequence[Tuple[str, str, str, Any]]):

        attribute_lookups = {}
        child_elements : Sequence[Optional[XmlElement]] = []

        for field in self.model_fields_set:

            field_data = getattr(self, field, None)
            if field_data is None or field in ['update_attribute', 'update_type', 'update_value']:
                continue

            if isinstance(field_data, XmlElement):
                child_elements.append(field_data)

            elif hasattr(field_data, '__iter__') and not isinstance(field_data, str):

                for inner_field in field_data:
                    if isinstance(inner_field, XmlElement):
                        child_elements.append(inner_field)
            else:
                attribute_lookups[field] = field_data

        curr_query = DetectorConfigXpath.create_tag_query(
            tag=self.element_tag, attributes=attribute_lookups
        )
        new_parent_queries = []
        for parent_query in parent_queries:

            new_query = parent_query + curr_query
            if len(child_elements) == 0:
                if self.update_attribute is None:
                    err = f"The update attribute for the bottom level xml element '{self.element_tag}' must be provided."
                    raise ValueError(err)
                if self.update_type is None:
                    err = f"The update type for the bottom level xml element '{self.element_tag}' must be provided."
                    raise ValueError(err)
                if self.update_type in ['SET', 'ADD'] and self.update_value is None:
                    err = f"The update value must be included for 'SET' and 'ADD' update types. Got {self.update_type}."
                    raise ValueError(err)
                query_tuple = (new_query, self.update_attribute, self.update_type, self.update_value)
                all_queries.append(query_tuple)
                new_parent_queries.append(new_query)

            elif self.update_attribute is not None and self.update_type is not None:
                if self.update_type in ['SET', 'ADD'] and self.update_value is None:
                    err = f"The update value must be included for 'SET' and 'ADD' update types. Got {self.update_type}."
                    raise ValueError(err)
                query_tuple = (new_query, self.update_attribute, self.update_type, self.update_value)
                all_queries.append(query_tuple)
                
            else:
                new_parent_queries.append(new_query)

        for child_elem in child_elements:

            child_elem._query_helper(new_parent_queries, all_queries)


XmlElementType = TypeVar('XmlElement', bound=XmlElement)

class XmlElementList(RootModel[XmlElement], Generic[XmlElementType]):

    model_config = ConfigDict(strict=True)
    root : SerializeAsAny[Sequence[XmlElementType]]

    def __iter__(self):
        return iter(self.root)
    
    def __getitem__(self, item):
        return self.root[item]

