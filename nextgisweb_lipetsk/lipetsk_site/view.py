# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import namedtuple
import json
from pyramid.response import Response
import shapely
from sqlalchemy.orm.exc import NoResultFound

from nextgisweb import DBSession
from .well_known_names import Maps, Layers, Fields
from nextgisweb.resource import Resource
from nextgisweb.vector_layer import VectorLayer
from nextgisweb.webmap import WebMap
from nextgisweb.webmap.plugin import WebmapPlugin
from nextgisweb.webmap.adapter import WebMapAdapter
from nextgisweb.webmap.util import _
import pyramid.httpexceptions as exc


def setup_pyramid(comp, config):

    config.add_static_view(
        name='lipetsk/static',
        path='nextgisweb_lipetsk:lipetsk_site/static', cache_max_age=3600)

    config.add_route(
        'lipetsk.site.main',
        '/lipetsk/main',
    ).add_view(show_main, renderer='nextgisweb_lipetsk:lipetsk_site/template/display.mako')

    config.add_route(
        'lipetsk.site.selected',
        '/lipetsk/selected',
    ).add_view(show_selected, renderer='nextgisweb_lipetsk:lipetsk_site/template/display.mako')

    config.add_route(
        'lipetsk.site.get_district_extent',
        '/lipetsk/get_district_extent/{id:\d+}',
    ).add_view(get_district_extent)


def show_main(request):
    try:
        obj = Resource.filter_by(keyname=Maps.PUBLIC_MAP).one()
    except NoResultFound:
        # TODO: сделать темплейт для страницы ошибки и вставить в экс, либо сделать переход
        raise exc.HTTPInternalServerError(u'Публичная карта не настроена! Обратитесь к администратору сервера ')
        #raise exc.HTTPFound(request.route_url("section1"))   # Redirect

    #request.resource_permission(WebMap.scope.webmap.display)

    MID = namedtuple('MID', ['adapter', 'basemap', 'plugin'])

    show_main.mid = MID(
        set(),
        set(),
        set(),
    )

    def traverse(item):
        data = dict(
            id=item.id,
            type=item.item_type,
            label=item.display_name
        )

        if item.item_type == 'layer':
            style = item.style
            layer = style.parent

            # При отсутствии необходимых прав пропускаем элемент веб-карты,
            # таким образом он просто не будет показан при отображении и
            # в дереве слоев

            # TODO: Security

            # if not layer.has_permission(
            #     request.user,
            #     'style-read',
            #     'data-read',
            # ):
            #     return None

            # Основные параметры элемента
            data.update(
                layerId=style.parent_id,
                styleId=style.id,
                visibility=bool(item.layer_enabled),
                transparency=item.layer_transparency,
                minScaleDenom=item.layer_min_scale_denom,
                maxScaleDenom=item.layer_max_scale_denom,
            )

            data['adapter'] = WebMapAdapter.registry.get(
                item.layer_adapter, 'image').mid
            show_main.mid.adapter.add(data['adapter'])

            # Плагины уровня слоя
            plugin = dict()
            for pcls in WebmapPlugin.registry:
                p_mid_data = pcls.is_layer_supported(layer, obj)
                if p_mid_data:
                    plugin.update((p_mid_data, ))

            data.update(plugin=plugin)
            show_main.mid.plugin.update(plugin.keys())

        elif item.item_type in ('root', 'group'):
            # Рекурсивно пробегаем по всем элементам, исключая те,
            # на которые нет необходимых прав доступа
            data.update(
                expanded=item.group_expanded,
                children=filter(
                    None,
                    map(traverse, item.children)
                )
            )

        return data

    tmp = obj.to_dict()

    config = dict(
        extent=tmp["extent"],
        rootItem=traverse(obj.root_item),
        mid=dict(
            adapter=tuple(show_main.mid.adapter),
            basemap=tuple(show_main.mid.basemap),
            plugin=tuple(show_main.mid.plugin)
        ),
        bookmarkLayerId=obj.bookmark_resource_id,
    )

    return dict(
        obj=obj,
        display_config=config,
        custom_layout=True
    )


def show_selected(request):
    try:
        obj = Resource.filter_by(keyname=Maps.PUBLIC_MAP).one()
    except NoResultFound:
        # TODO: сделать темплейт для страницы ошибки и вставить в экс, либо сделать переход
        raise exc.HTTPInternalServerError(u'Публичная карта не настроена! Обратитесь к администратору сервера ')
        #raise exc.HTTPFound(request.route_url("section1"))   # Redirect

    active_groups = request.GET.getall('group')
    #request.resource_permission(WebMap.scope.webmap.display)

    MID = namedtuple('MID', ['adapter', 'basemap', 'plugin'])

    show_main.mid = MID(
        set(),
        set(),
        set(),
    )

    def traverse(item):
        data = dict(
            id=item.id,
            type=item.item_type,
            label=item.display_name
        )

        if item.item_type == 'layer':
            style = item.style
            layer = style.parent

            # visibility
            if item.parent and item.parent.item_type == 'group':
                vis = item.parent.display_name in active_groups
            else:
                vis = False

            # Основные параметры элемента
            data.update(
                layerId=style.parent_id,
                styleId=style.id,
                visibility=vis,
                transparency=item.layer_transparency,
                minScaleDenom=item.layer_min_scale_denom,
                maxScaleDenom=item.layer_max_scale_denom,
            )

            data['adapter'] = WebMapAdapter.registry.get(
                item.layer_adapter, 'image').mid
            show_main.mid.adapter.add(data['adapter'])

            # Плагины уровня слоя
            plugin = dict()
            for pcls in WebmapPlugin.registry:
                p_mid_data = pcls.is_layer_supported(layer, obj)
                if p_mid_data:
                    plugin.update((p_mid_data, ))

            data.update(plugin=plugin)
            show_main.mid.plugin.update(plugin.keys())

        elif item.item_type in ('root', 'group'):
            # Рекурсивно пробегаем по всем элементам, исключая те,
            # на которые нет необходимых прав доступа
            data.update(
                expanded=item.group_expanded,
                children=filter(
                    None,
                    map(traverse, item.children)
                )
            )

        return data

    tmp = obj.to_dict()

    config = dict(
        extent=tmp["extent"],
        rootItem=traverse(obj.root_item),
        mid=dict(
            adapter=tuple(show_main.mid.adapter),
            basemap=tuple(show_main.mid.basemap),
            plugin=tuple(show_main.mid.plugin)
        ),
        bookmarkLayerId=obj.bookmark_resource_id,
    )

    return dict(
        obj=obj,
        display_config=config,
        custom_layout=True
    )


def get_districts():
    db_session = DBSession()
    try:
        distr_res = db_session.query(Resource).filter(Resource.keyname == Layers.DISTRICTS, Resource.cls == VectorLayer.identity).one()
    except NoResultFound:
        #raise exc.HTTPInternalServerError(u'Публичная карта не настроена! Обратитесь к администратору сервера')
        #raise exc.HTTPFound(request.route_url("section1"))   # Redirect
        return []


    query = distr_res.feature_query()
    features = query()

    result = []
    for feature in features:
        result.append({'id': feature.id, 'district': feature.fields[Fields.DISTRICT_NAME]})
    return result


def get_district_extent(request):
    dist_id = request.matchdict['id']
    if dist_id is None:
        return Response('[]')

    db_session = DBSession()

    try:
        distr_res = db_session.query(Resource).filter(Resource.keyname == Layers.DISTRICTS, Resource.cls == VectorLayer.identity).one()
    except NoResultFound:
        raise exc.HTTPInternalServerError(u'Публичная карта не настроена! Обратитесь к администратору сервера')

    try:
        query = distr_res.feature_query()
        query.geom()
        query.filter_by(id=int(dist_id))
        for feat in query():
            extent = feat.geom.bounds
            break
    except:
        raise exc.HTTPInternalServerError(u'Район с заданныи id не найден! Обратитесь к администратору сервера')

    resp = {'extent': extent}

    return Response(json.dumps(resp))
