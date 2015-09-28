# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .lipetsk_manage import command  # NOQA


def pkginfo():
    return dict(
        components=dict(
            lipetsk_site='nextgisweb_lipetsk.lipetsk_site',
        )
    )


def amd_packages():
    return (
        ('ngw-lipetsk-site', 'nextgisweb_lipetsk:lipetsk_site/amd/ngw-lipetsk-site'),
    )
