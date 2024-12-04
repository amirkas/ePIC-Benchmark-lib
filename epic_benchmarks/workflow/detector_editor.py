from epic_benchmarks._constants import *
from epic_benchmarks.configurations.utils import XmlEditor
from epic_benchmarks.workflow.manager import ParslWorkflowManager

def edit_detector(manager : ParslWorkflowManager, benchmark_name : str, detector_config : dict):

    detector_file = detector_config[DETECTOR_FILE_KEY]
    detector_path = manager.detector_description_path(benchmark_name, detector_file)
    editor = XmlEditor(detector_path, autosave=True)
    xpath_query = ""
    if DETECTOR_NAME_KEY in detector_config.keys():
        detector_name = detector_config[DETECTOR_NAME_KEY]
        xpath_query += "//{tag}[@{attr}='{name}']".format(
            tag=XPATH_DETECTOR_TAG,
            attr=XPATH_DETECTOR_NAME_ATTR,
            name=detector_name
        )
    if DETECTOR_MODULE_KEY in detector_config.keys():
        module_name = detector_config[DETECTOR_MODULE_KEY]
        xpath_query += "//{tag}[@{attr}='{name}']".format(\
            tag=XPATH_MODULE_TAG,
            attr=XPATH_MODULE_NAME_ATTR,
            name=module_name
        )
    if DETECTOR_MODULE_COMPONENT_KEY in detector_config.keys():
        component_name = detector_config[DETECTOR_MODULE_COMPONENT_KEY]
        xpath_query += "//{tag}[@{attr}='{name}']".format(\
            tag=XPATH_COMPONENT_TAG,
            attr=XPATH_COMPONENT_NAME_ATTR,
            name=component_name
        )

    edit_type = detector_config[DETECTOR_TYPE_KEY]
    if edit_type == "set":
        edit_attribute = detector_config[DETECTOR_ATTRIBUTE_KEY]
        edit_value = detector_config[DETECTOR_VALUE_KEY]
        print(xpath_query)
        print(edit_attribute)
        print(edit_value)
        editor.set_attribute_xpath(xpath_query, edit_attribute, edit_value)


def edit_all_detectors(manager : ParslWorkflowManager, benchmark_name : str):

    detector_configs = manager.get_detector_config_list(benchmark_name)
    for config in detector_configs:
        edit_detector(manager, benchmark_name=benchmark_name, detector_config=config.get_config_dict())


