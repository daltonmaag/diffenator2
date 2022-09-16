#!/usr/bin/env python3
# Copyright 2016 The Fontbakery Authors
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
#
import requests
from io import BytesIO
from zipfile import ZipFile
import sys
import os
import shutil
import unicodedata
from collections import namedtuple
from pkg_resources import resource_filename
import json
from PIL import Image
if sys.version_info[0] == 3:
    from configparser import ConfigParser
else:
    from ConfigParser import ConfigParser

# =====================================
# HELPER FUNCTIONS


## Font-related utility functions

def font_stylename(ttFont):
    """Get a font's stylename using the name table. Since our fonts use the
    RIBBI naming model, use the Typographic SubFamily Name (NAmeID 17) if it
    exists, otherwise use the SubFamily Name (NameID 2).

    Args:
        ttFont: a TTFont instance
    """
    return get_name_record(ttFont, 17, fallbackID=2)


def font_familyname(ttFont):
    """Get a font's familyname using the name table. since our fonts use the
    RIBBI naming model, use the Typographic Family Name (NameID 16) if it
    exists, otherwise use the Family Name (Name ID 1).

    Args:
        ttFont: a TTFont instance
    """
    return get_name_record(ttFont, 16, fallbackID=1)


def get_name_record(ttFont, nameID, fallbackID=None, platform=(3, 1, 0x409)):
    """Return a name table record which has the specified nameID.

    Args:
        ttFont: a TTFont instance
        nameID: nameID of name record to return,
        fallbackID: if nameID doesn't exist, use this nameID instead
        platform: Platform of name record. Default is Win US English

    Returns:
        str
    """
    name = ttFont["name"]
    record = name.getName(nameID, 3, 1, 0x409)
    if not record and fallbackID:
        record = name.getName(fallbackID, 3, 1, 0x409)
    if not record:
        raise ValueError(f"Cannot find record with nameID {nameID}")
    return record.toUnicode()


def font_is_italic(ttfont):
    """Check if the font has the word "Italic" in its stylename."""
    stylename = ttfont["name"].getName(2, 3, 1, 0x409).toUnicode()
    return True if "Italic" in stylename else False


def gen_gifs(dir1, dir2, dst_dir):
    dir1_imgs = set(f for f in os.listdir(dir1) if f.endswith(("jpg", "png")))
    dir2_imgs = set(f for f in os.listdir(dir2) if f.endswith(("jpg", "png")))
    shared_imgs = dir1_imgs & dir2_imgs
    for img in shared_imgs:
        gif_filename = img[:-4] + '.gif'
        img_a_path = os.path.join(dir1, img)
        img_b_path = os.path.join(dir2, img)
        dst = os.path.join(dst_dir, gif_filename)
        gen_gif(img_a_path, img_b_path, dst)


def gen_gif(img_a_path, img_b_path, dst):
    with Image.open(img_a_path) as img_a, Image.open(img_b_path) as img_b:
        img_a.save(
            dst, 
            save_all=True,
            append_images=[img_b],
            loop=10000,
            duration=1000
        )


def partition(items, size):
    """partition([1,2,3,4,5,6], 2) --> [[1,2],[3,4],[5,6]]"""
    return [items[i : i + size] for i in range(0, len(items), size)]

