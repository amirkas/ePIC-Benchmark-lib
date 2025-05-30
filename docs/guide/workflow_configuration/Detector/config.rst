DetectorConfig
--------------

The **DetectorConfig** object is used to dynamically alter the ePIC detector geometry before its compilation. 

The following are the required attributes of the **DetectorConfig** object:

* **file** - The relative path of the detector geometry description XML file to be updated with respect to the ePIC repository's **compact** directory. 
* **edit_element_trees** - An **XmlElement** tree or list of **XmlElement** Trees used to search for XML elements and define how they're updated. 