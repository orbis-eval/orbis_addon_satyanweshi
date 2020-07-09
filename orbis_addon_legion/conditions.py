# -*- coding: utf-8 -*-

conditions = {
    "simple": [
        "same_url",
        "same_type",
        "same_surfaceForm"
    ],
    "strict": [
        "same_start",
        "same_end",
        "same_url",
        "same_type",
        "same_surfaceForm"
    ],
    "overlap_withtype": [
        "overlap",
        "same_url",
        "same_type"
    ],
    "overlap": [
        "overlap",
        "same_url"
    ],
    "simple_ner": [
        "overlap",
        "same_type",
    ],
    "strict_ner": [
        "same_start",
        "same_end",
        "same_type",
    ]
}
