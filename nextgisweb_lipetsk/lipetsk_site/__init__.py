# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from nextgisweb import Base
from nextgisweb.component import Component

from .ident import COMP_ID


@Component.registry.register
class LipetskSiteComponent(Component):
    identity = COMP_ID
    metadata = Base.metadata

    def initialize(self):
        super(LipetskSiteComponent, self).initialize()

    def setup_pyramid(self, config):
        super(LipetskSiteComponent, self).setup_pyramid(config)

        from . import view
        view.setup_pyramid(self, config)

    settings_info = (
    )
