from dataclasses import dataclass

@dataclass    
class DetectorConfigXpath:

    ROOT_TAG : str = "."
    DETECTOR_TAG : str = "detector"
    MODULE_TAG : str = "module"
    COMPONENT_TAG : str = "module_component"
    CONSTANT_TAG : str = "constant"
    READOUT_TAG : str = "readout"
    SEGMENTATION_TAG : str = "segmentation"

    #Generates the xpath query for a single xml tag with 1 or more attributes
    #to search against.
    @classmethod
    def create_tag_query(cls, tag, attributes, case_sensitive=False) -> str:
        if not isinstance(attributes, dict) and attributes is not None:
            err = f"attributes must be a dictionary or None: Got type: {type(attributes)}"
            raise ValueError(err)
        if len(tag) == 0 or attributes is None or len(attributes) == 0:
            return ""
        query = f'//{tag}'
        if len(attributes.keys()) > 0:
            if case_sensitive:
                attr_str = lambda item : f"@{item[0]}='{item[1]}'"
            else:
                attr_str = lambda item : f"translate(@{item[0]}, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = '{str(item[1]).lower()}'"
            all_attr_str = " && ".join(map(attr_str, list(attributes.items())))
            query += f'[{all_attr_str}]'
        return query
    
    #Generates and concatenates individual xpath queries for each tag
    @classmethod
    def create_generic_query(cls, query_elems : dict) -> str:

        combined_query = ''
        for tag, attributes in query_elems.items():
            if tag is not None:
                combined_query += cls.create_tag_query(tag, attributes)
        return combined_query
    
    #Generates the entire search xpath search query for a detector description file
    @classmethod
    def create_query(
            cls,
            detector_attributes, 
            module_attributes, 
            module_component_attributes, 
            constant_attributes,
            readout_attributes, 
            segmentation_attributes
            ):
        return cls.create_generic_query(
            {
            cls.DETECTOR_TAG : detector_attributes,
            cls.MODULE_TAG : module_attributes,
            cls.COMPONENT_TAG : module_component_attributes,
            cls.CONSTANT_TAG : constant_attributes,
            cls.READOUT_TAG : readout_attributes,
            cls.SEGMENTATION_TAG : segmentation_attributes,
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
    