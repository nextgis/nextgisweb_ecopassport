# -*- coding: utf-8 -*-
from .lipetsk_manage import command  # NOQA


def pkginfo():
    return dict(
        components=dict(
            lipetsk_site='nextgisweb_lipetsk.lipetsk_site',
            lipetsk_manage='nextgisweb_lipetsk.lipetsk_manage',
        )
    )


def amd_packages():
    return (
        ('ngw-lipetsk-site', 'nextgisweb_lipetsk:lipetsk_site/amd/ngw-lipetsk-site'),
    )
