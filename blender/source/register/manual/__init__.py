from . import (
    property_groups_reference,
    operator_references
)

manual_prefix = "https://x-hax.github.io/SonicAdventureBlenderIODocs/"
manual_mapping = []

manual_mapping.extend(property_groups_reference.manual_mapping)
manual_mapping.extend(operator_references.manual_mapping)


def add_manual_map():
    return manual_prefix, manual_mapping
