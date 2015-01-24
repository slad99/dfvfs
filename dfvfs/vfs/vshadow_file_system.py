# -*- coding: utf-8 -*-
"""The Volume Shadow Snapshots (VSS) file system implementation."""

# This is necessary to prevent a circular import.
import dfvfs.vfs.vshadow_file_entry

from dfvfs.lib import definitions
from dfvfs.lib import vshadow
from dfvfs.path import vshadow_path_spec
from dfvfs.vfs import file_system


class VShadowFileSystem(file_system.FileSystem):
  """Class that implements a file system object using pyvshadow."""

  LOCATION_ROOT = u'/'
  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VSHADOW

  def __init__(self, resolver_context, vshadow_volume, path_spec):
    """Initializes the file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      vshadow_volume: the VSS volume object (instance of pyvshadow.volume).
      path_spec: the path specification (instance of path.PathSpec) of
                 the file-like object.
    """
    super(VShadowFileSystem, self).__init__(resolver_context)
    self._vshadow_volume = vshadow_volume
    self._path_spec = path_spec

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      Boolean indicating if the file entry exists.
    """
    store_index = vshadow.VShadowPathSpecGetStoreIndex(path_spec)

    # The virtual root file has not corresponding store index but
    # should have a location.
    if store_index is None:
      location = getattr(path_spec, 'location', None)
      return location is not None and location == self.LOCATION_ROOT

    return (store_index >= 0 and
            store_index < self._vshadow_volume.number_of_stores)

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      A file entry (instance of vfs.VShadowFileEntry) or None.
    """
    store_index = vshadow.VShadowPathSpecGetStoreIndex(path_spec)

    # The virtual root file has not corresponding store index but
    # should have a location.
    if store_index is None:
      location = getattr(path_spec, 'location', None)
      if location is None or location != self.LOCATION_ROOT:
        return
      return self.GetRootFileEntry()

    if store_index < 0 or store_index >= self._vshadow_volume.number_of_stores:
      return
    return dfvfs.vfs.vshadow_file_entry.VShadowFileEntry(
        self._resolver_context, self, path_spec)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry).
    """
    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=self.LOCATION_ROOT, parent=self._path_spec)
    return dfvfs.vfs.vshadow_file_entry.VShadowFileEntry(
        self._resolver_context, self, path_spec, is_root=True, is_virtual=True)

  def GetVShadowVolume(self):
    """Retrieves the VSS volume object.

    Returns:
      The VSS volume object (instance of pyvshadow.volume).
    """
    return self._vshadow_volume
