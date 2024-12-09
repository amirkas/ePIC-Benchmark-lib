#!/usr/bin/env python
# coding: utf-8

import yaml
from lxml import etree

class YamlEditor:
    
    def __init__(self, file_path):
        with open(file_path, 'r') as f:
            self.content = yaml.safe_load(f)
            self.file_path = file_path
    
    def get_elem(self, key_path):
        
        path = key_path.split(".")
        curr_path = ""
        curr_node = self.content
        #Traverse tree until node that contains elem is reached.
        for key in path:
            if (key not in curr_node.keys()):
                raise Exception(curr_path + " not found")
            else:
                curr_node = curr_node[key]
                
        #Return value of found node.
        return curr_node
            
                                
    def set_elem(self, key_path, elem):
        path = key_path.split(".")
        curr_path = ""
        curr_node = self.content
        
        #Traverse tree until the parent node of the desired elem is reached.
        for key in path[:-1]:
            print(key)
            curr_path += ("." + key)
            if (key not in curr_node.keys()):
                raise Exception(curr_path + " not found")
            else:
                curr_node = curr_node[key]
                
        #Set value at desired path
        curr_node[path[-1]] = elem
                                
    def add_elem(self, key_path, elem):
        path = key_path.split(".")
        curr_path = ""
        curr_node = self.content
        
        #Traverse tree until parent node of the desired elem is reached.
        for key in path[:-1]:

            curr_path += ("." + key)
            if (key not in curr_node.keys()):
                raise Exception(curr_path + " not found")
            else:
                curr_node = curr_node[key]
                
        #Set value at desired path
        curr_node[path[-1]] = elem
                                
    def save_as(self, new_filepath):
        
        with open(new_filepath, 'w') as writeable:
            yaml.dump(self.content, writeable)
        
    def save(self):
        self.save_as(self.file_path)
       
                                              
def tag_to_xpath(tags=""):
    if len(tags) == 0:
        return ""
    if isinstance(tags, str):
        if not tags.startswith("//") and not tags.startswith(".//"):
            return '//{t}'.format(t=tags)
        else:
            return tags
    elif isinstance(tags, list):
        path=""
        for tag in tags:
            path += tag_to_xpath(tag)
        return path
    else:
        return ""


def attribute_to_xpath(attribute, value):
    if len(attribute) == 0:
        return ""
    if (value == None):
        return '@{a}'.format(a=attribute)
    return '@{a}="{val}"'.format(a=attribute, val=value)

def attribute_dict_to_xpath(attribute_dict={}):
    attribute_str = ""
    attributes = list(attribute_dict.keys())

    if (len(attributes) == 0):
        return ""
    
    for attribute in attributes[:-1]:
        attribute_str += attribute_to_xpath(attribute, attribute_dict[attribute])
        attribute_str += (" and ")
    last_attribute = attributes[-1]
    attribute_str += attribute_to_xpath(last_attribute, attribute_dict[last_attribute])
    
    return "[{all}]".format(all=attribute_str)


def autosave(func):
    def wrapper(self, *args, **kw):
        #Call function before post-processing
        out = func(self, *args, **kw)
        #Auto save post processing
        if (self.autosave):
            self.save()
        return out
    return wrapper

class XmlEditor:

    def __init__(self, filepath, autosave=False):

        try:
            self.tree = etree.parse(filepath)
            self.root = self.tree.getroot()
            self.filepath = filepath
            self.autosave = autosave
        except:
            raise Exception("No XML File found at: " + str(filepath))
        
    def get_root(self):
        return self.root
        
    def save(self, filepath=""):
        if (len(filepath) == 0):
            to_save = self.filepath
        else:
            to_save = filepath          
        try:
            self.tree.write(to_save, xml_declaration=True)
        except:
            print("Could not save file at: " + to_save)    

    def get_elements(self, ancestor_tag_="", ancestor_attributes_={}, element_tag_="//*", element_attributes_={}):

        
        #Format attributes for xml.eTree findall function call.

        full_xpath = ""
        full_xpath += (tag_to_xpath(ancestor_tag_))
        full_xpath += (attribute_dict_to_xpath(ancestor_attributes_))
        full_xpath += (tag_to_xpath(element_tag_))
        full_xpath += (attribute_dict_to_xpath(element_attributes_))

        print(full_xpath)
        found_keys = self.root.xpath(full_xpath)
        
        if len(found_keys) == 0:
            raise Exception(f"Could not find path: {full_xpath}")
        elif len(found_keys) == 1:
            return found_keys[0]
        else:
            elements = []
            for element in found_keys:
                elements.append(element)
            return elements

    def get_val(self, ancestor_tag="", ancestor_attributes={}, element_tag="//*", element_attributes={}):

        elems = []
        for element in self.get_elements(ancestor_tag_=ancestor_tag, ancestor_attributes_=ancestor_attributes, element_tag_=element_tag, element_attributes_=element_attributes):
            elems.append(element.text)
        return elems

    @autosave
    def set_text(self, text, ancestor_tag="", ancestor_attributes={}, element_tag="//*", element_attributes={}):

        for element in self.get_elements(ancestor_tag_=ancestor_tag, ancestor_attributes_=ancestor_attributes, element_tag_=element_tag, element_attributes_=element_attributes):
            element.text = text

    @autosave
    def set_attribute(self, attr, val, ancestor_tag="", ancestor_attributes={}, element_tag="//*", element_attributes={}):

        for element in self.get_elements(ancestor_tag_=ancestor_tag, ancestor_attributes_=ancestor_attributes, element_tag_=element_tag, element_attributes_=element_attributes):
            element.set(attr, val)

    @autosave
    def add_element(self, new_tag, new_text, new_attributes={}, parent_tag="//*", parent_attributes={}, ancestor_tag="", ancestor_attributes={}):
        new_element = etree.Element(new_tag)
        new_element.text = new_text
        for attr in new_attributes.keys():
            new_element.set(attr, new_attributes[attr])
        for element in self.get_elements(ancestor_tag_=ancestor_tag, ancestor_attributes_=ancestor_attributes, element_tag_=parent_tag, element_attributes_=parent_attributes):
            element.append(new_element)

    @autosave
    def set_attribute_xpath(self, xpath_query, attribute, value):

        found_elems = self.root.xpath(xpath_query)
        for elem in found_elems:
            elem.set(attribute, value)
        



    
            
    
