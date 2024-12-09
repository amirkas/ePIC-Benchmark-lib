from dataclasses import dataclass

@dataclass    
class DetectorConfigXpath:

    ROOT_TAG : str = "."
    DETECTOR_TAG : str = "detector"
    MODULE_TAG : str = "module"
    COMPONENT_TAG : str = "module_component"

    @classmethod
    def create_tag_query(cls, tag, attributes) -> str:
        if not isinstance(attributes, dict):
            raise ValueError("attributes must be a dictionary: Got type: ", type(attributes))
        if len(tag) == 0:
            return ""
        query = f'//{tag}'
        if len(attributes.keys()) > 0:
            attr_str = lambda item : f"@{item[0]}='{item[1]}'"
            all_attr_str = " && ".join(map(attr_str, list(attributes.items())))
            query += f'[{all_attr_str}]'
        return query
    
    @classmethod
    def create_generic_query(cls, query_elems : dict) -> str:

        combined_query = ''
        for tag, attributes in query_elems.items():
            combined_query += cls.create_tag_query(tag, attributes)
        return combined_query
    
    @classmethod
    def create_query(cls, detector_attributes, module_attributes, module_component_attributes):
        return cls.create_generic_query(
            {
            cls.DETECTOR_TAG : detector_attributes,
            cls.MODULE_TAG : module_attributes,
            cls.COMPONENT_TAG : module_component_attributes
            }
        )

    
    @classmethod
    def detector_tag_query(cls, attributes):
        return cls.create_tag_query(cls.DETECTOR_TAG, attributes)
    
    
    @classmethod
    def module_tag_query(cls, attributes):
        return cls.create_tag_query(cls.MODULE_TAG, attributes)
    
    @classmethod
    def module_component_tag_query(cls, attributes):
        return cls.create_tag_query(cls.COMPONENT_TAG, attributes)
    