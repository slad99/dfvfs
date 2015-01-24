# -*- coding: utf-8 -*-
"""The Volume Shadow Snapshots (VSS) format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class VShadowAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """Class that implements the VSS analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_VOLUME_SYSTEM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VSHADOW

  def GetFormatSpecification(self):
    """Retrieves the format specification."""
    format_specification = specification.Specification(self.type_indicator)

    # VSS identifier (GUID).
    format_specification.AddNewSignature(
        b'\x6b\x87\x08\x38\x76\xc1\x48\x4e\xb7\xae\x04\x04\x6e\x6c\xc7\x52',
        offset=7680)

    return format_specification


# Register the analyzer helpers with the analyzer.
analyzer.Analyzer.RegisterHelper(VShadowAnalyzerHelper())
