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
"""Tests for the volume system implementation using pyvshadow."""

import os
import unittest

from pyvfs.path import os_path_spec
from pyvfs.path import qcow_path_spec
from pyvfs.path import vshadow_path_spec
from pyvfs.volume import vshadow_volume_system


class VShadowVolumeSystemTest(unittest.TestCase):
  """The unit test for the Volume Shadow Snapshot (VSS) volume system object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = os.path.join('test_data', 'vsstest.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = qcow_path_spec.QcowPathSpec(parent=path_spec)
    self._vshadow_path_spec = vshadow_path_spec.VShadowPathSpec(
        parent=path_spec)

  # qcowmount test_data/vsstest.qcow2 fuse/
  # vshadowinfo fuse/qcow1
  #
  # Volume Shadow Snapshot information:
  #   Number of stores: 2
  #
  # Store: 1
  #   ...
  #   Identifier                : 600f0b69-5bdf-11e3-9d6c-005056c00008
  #   Shadow copy set ID        : 0a4e3901-6abb-48fc-95c2-6ab9e38e9e71
  #   Creation time             : Dec 03, 2013 06:35:09.736378700 UTC
  #   Shadow copy ID            : 4e3c03c2-7bc6-4288-ad96-c1eac1a55f71
  #   Volume size               : 1073741824 bytes
  #   Attribute flags           : 0x00420009
  #
  # Store: 2
  #   Identifier                : 600f0b6d-5bdf-11e3-9d6c-005056c00008
  #   Shadow copy set ID        : 8438a0ee-0f06-443b-ac0c-2905647ca5d6
  #   Creation time             : Dec 03, 2013 06:37:48.919058300 UTC
  #   Shadow copy ID            : 18f1ac6e-959d-436f-bdcc-e797a729e290
  #   Volume size               : 1073741824 bytes
  #   Attribute flags           : 0x00420009

  def testIterateVolumes(self):
    """Test the iterate volumes functionality."""
    volume_system = vshadow_volume_system.VShadowVolumeSystem()

    volume_system.Open(self._vshadow_path_spec)

    self.assertEquals(volume_system.number_of_volumes, 2)

    volume = volume_system.GetVolumeByIndex(1)

    self.assertEquals(volume.number_of_extents, 1)
    self.assertEquals(volume.number_of_attributes, 4)
    self.assertEquals(volume.identifier, 'vss2')


if __name__ == '__main__':
  unittest.main()
