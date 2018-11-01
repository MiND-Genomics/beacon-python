"""Info Endpoint.

Querying the info endpoint reveals information about existing datasets in this beacon
and their associated metadata.

.. note:: See ``beacon_api`` root folder ``__init__.py`` for changing values used here.
"""

from .. import __apiVersion__, __title__, __version__, __description__, __url__, __alturl__
from .. import __createtime__, __updatetime__, __org_id__, __org_name__, __org_description__
from .. import __org_address__, __org_logoUrl__, __org_welcomeUrl__, __org_info__, __org_contactUrl__
from ..utils.data_query import fetch_dataset_metadata


async def beacon_info(host, pool):
    """Construct the `Beacon` app information dict.

    :return beacon_info: A dict that contain information about the ``Beacon`` endpoint.
    """
    beacon_dataset = await fetch_dataset_metadata(pool)

    # TO DO provide more meaninful example specific to the endpoint data
    sample_allele_request = [{
        "alternateBases": "C",
        "referenceBases": "T",
        "referenceName": "MT",
        "start": 10,
        "assemblyId": "GRCh38",
        "includeDatasetResponses": "ALL"
    }, {
        "alternateBases": "A",
        "referenceBases": "G",
        "referenceName": "MT",
        "start": 7600,
        "assemblyId": "GRCh38",
        "datasetIds": [
            "urn:hg:exampleid-mt"
        ],
        "includeDatasetResponses": "HIT"},
        {
        "variantType": "SNP",
        "referenceBases": "T",
        "referenceName": "Y",
        "start": 7267244,
        "assemblyId": "GRCh38"
    }
    ]

    organization = {
        'id': __org_id__,
        'name': __org_name__,
        'description': __org_description__,
        'address': __org_address__,
        'welcomeUrl': __org_welcomeUrl__,
        'contactUrl': __org_contactUrl__,
        'logoUrl': __org_logoUrl__,
        'info': __org_info__,
    }

    beacon_info = {
        # TO DO implement some faillback mechanism for ID
        'id': '.'.join(reversed(host.split('.'))),
        'name': __title__,
        'apiVersion': __apiVersion__,
        'organization': organization,
        'description': __description__,
        'version': __version__,
        'welcomeUrl': __url__,
        'alternativeUrl': __alturl__,
        'createDateTime': __createtime__,
        'updateDateTime': __updatetime__,
        'datasets': beacon_dataset,
        'sampleAlleleRequests': sample_allele_request,
        'info': {}
    }

    return beacon_info