XML Element Search
------------------

Each detector geometry file in the ePIC repository has a tree-like structure of XML elements with different tags and attributes.
Making changes to an XML element requires that a query be constructed to find the XML element of interest.
This library manages query construction for you, but you must define the XML Element tree associated with the query.
This is done with the use of **XmlElement** objects defined in the submodules of **ePIC_benchmarks.detector.xml_elements** to construct an **XmlElement** Tree. 

The list and hierarchical structure of available XML elements for use for each submodule are as follows:

XML Elements
------------

Detector XML Elements
^^^^^^^^^^^^^^^^^^^^^

* XmlDetectorElement

  * XmlModuleElement

    * XmlModuleComponentElement

    * XmlTrdElement

    * XmlFrameElement

  * XmlLayerElement

    * XmlLayerMaterialElement

    * XmlRphiLayoutElement

    * XmlBarrelEnvelopeElement

    * XmlZLayoutElement

    * XmlEnvelopeElement

    * XmlRingElement

  * XmlDimensionsElement

  * XmlTypeFlagsElement

Constant XML Elements
^^^^^^^^^^^^^^^^^^^^^^

* XmlConstantElement

Plugin XML Elements
^^^^^^^^^^^^^^^^^^^^^^

* XmlArgumentElement

* XmlPluginElement

Readout XML elements
^^^^^^^^^^^^^^^^^^^^^^

* XmlReadoutElement

  * XmlSegmentationElement

* XmlReadoutIdElement

Constructing an XML Element Tree
--------------------------------

To construct a query such that for **every XmlModuleComponentElement**
of **every XmlModuleElement** of **every XmlDetectorElement**, the **XmlModuleComponentElement's** **'sensitive'** attribute is updated to be **false**,
we would define the following **XmlElement** tree:

.. code-block:: python

    XmlDetectorElement(
        modules=XmlModuleElement(
            module_components=XmlModuleComponentElement(
                update_attribute="sensitive",
                update_value="false",
                update_type='SET'
            )
        )
    )

Whereas to construct a query where the **'sensitive'** attribute of 
the **XmlModuleComponentElement** with **material="Silicon"** belonging to
the **XmlModuleElement** with **name="Module1"** belonging to
the **XmlDetectorElement** with **name="InnterTrackerEndcapP"** is updated to be **false**,
we would define the following **XmlElement** tree:

.. code-block:: python

    XmlDetectorElement(
        name="InnerTrackerEndcapP",
        modules=XmlModuleElement(
            name="Module1",
            module_components=XmlModuleComponentElement(
                material="Silicon",
                update_attribute="sensitive",
                update_value="false",
                update_type='SET'
            )
        )
    )

.. note::
    All of the leaf nodes of an **XmlElement** tree must have non-None values for its **update_type** and the **update_attribute** parameters.

To integrate this example of an detector geometry update into a workflow for the **tracking/silicon_disks.xml** detector description file,
we would initialize the following DetectorConfig object:

.. code-block:: python

    from ePIC_benchmarks.detector import DetectorConfig
    from ePIC_benchmarks.detector.xml_elements.detector import (
        XmlDetectorElement, XmlModuleElement, XmlModuleComponentElement
    )

    EXAMPLE_DETECTOR_CONFIG = DetectorConfig(
        file="tracking/silicon_disks.xml",
        edit_element_trees=XmlDetectorElement(
            name="InnerTrackerEndcapP",
            modules=XmlModuleElement(
                name="Module1",
                module_components=XmlModuleComponentElement(
                    material="Silicon",
                    update_attribute="sensitive",
                    update_value="false",
                    update_type='SET'
                )
            )
        )
    )

Detector Geometry Update Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The value of an XML element's **'update_type'** defines the way that an XML Element attribute is updated.
The value of an XML element's **'update_attribute'** states the attribute that should be updated.
The value of an XML element's **'update_value'** states the value that the attribute given in **'update_attribute'** should be updated with.

The currently allowed **update_types** are as follows:

* **SET** - Set the value of the attribute given in **'update_attribute'** to the the value given in **'update_value'**.
* **ADD** - Add the value given in **'update_value'** to the already existing value of the attribute given in **'update_attribute'**.
* **DELETE** - Delete the attribute given in **'update_attribute'** from the Xml Element. 