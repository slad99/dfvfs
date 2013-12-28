#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The PyVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for the partition file entry implementation using the pytsk3."""

import os
import unittest

import pytsk3

from pyvfs.file_io import os_file_io
from pyvfs.lib import tsk_image
from pyvfs.path import os_path_spec
from pyvfs.path import tsk_partition_path_spec
from pyvfs.vfs import tsk_partition_file_entry
from pyvfs.vfs import tsk_partition_file_system


class TSKPartitionFileEntryTest(unittest.TestCase):
  """The unit test for the TSK partition file entry object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = os.path.join('test_data', 'tsk_volume_system.raw')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    file_object = os_file_io.OSFile()
    file_object.open(self._os_path_spec)
    tsk_image_object = tsk_image.TSKFileSystemImage(file_object)
    tsk_volume = pytsk3.Volume_Info(tsk_image_object)
    self._tsk_file_system = tsk_partition_file_system.TSKPartitionFileSystem(
        tsk_volume, self._os_path_spec)

  # mmls test_data/tsk_volume_system.raw
  # DOS Partition Table
  # Offset Sector: 0
  # Units are in 512-byte sectors
  #
  #      Slot    Start        End          Length       Description
  # 00:  Meta    0000000000   0000000000   0000000001   Primary Table (#0)
  # 01:  -----   0000000000   0000000000   0000000001   Unallocated
  # 02:  00:00   0000000001   0000000350   0000000350   Linux (0x83)
  # 03:  Meta    0000000351   0000002879   0000002529   DOS Extended (0x05)
  # 04:  Meta    0000000351   0000000351   0000000001   Extended Table (#1)
  # 05:  -----   0000000351   0000000351   0000000001   Unallocated
  # 06:  01:00   0000000352   0000002879   0000002528   Linux (0x83)

  def testIntialize(self):
    """Test the initialize functionality."""
    file_entry = tsk_partition_file_entry.TSKPartitionFileEntry(
        self._tsk_file_system, self._os_path_spec)

    self.assertNotEquals(file_entry, None)

  def testGetParentFileEntry(self):
    """Test the get parent file entry functionality."""
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=1, parent=self._os_path_spec)
    file_entry = self._tsk_file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertEquals(parent_file_entry, None)

  def testSubFileEntries(self):
    """Test the sub file entries iteration functionality."""
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=u'/', parent=self._os_path_spec)
    file_entry = self._tsk_file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)

    expected_sub_file_entry_names = [u'', u'', u'', u'', u'', u'p1', u'p2']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEquals(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEquals(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))


if __name__ == '__main__':
  unittest.main()
