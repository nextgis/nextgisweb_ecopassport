define([
    'dojo/_base/declare',
    'dojo/_base/lang',
    'dojo/aspect',
    'dojo/dom-style',
    'dojo/topic',
    'dojo/Deferred',
    'dojo/request/xhr',
    'dojo/dom-construct',
    'dojo/query',
    'dijit/registry',
    'dgrid/OnDemandGrid',
    'dgrid/extensions/ColumnResizer',
    'dojo/store/Memory',
    'dgrid/Selection',
    // settings
    "ngw/settings!lipetsk_site"
], function (declare, lang, aspect, domStyle, topic, Deferred, xhr, domConstruct, query, registry,
             OnDemandGrid, ColumnResizer, Memory, Selection, clientSettings) {
    return declare(null, {

        _columns: {
                district: 'Муниципальный район'
        },

        _get_extent_url: ngwConfig.applicationUrl + '/lipetsk/get_district_extent',


        constructor: function (domId) {
            districts = clientSettings.districts;
            this._store = Memory({data: districts});

            //grid
            this._grid = new (declare([OnDemandGrid, ColumnResizer, Selection]))(
                {
                    store: this._store,
                    columns: this._columns,
                    selectionMode: 'single',
                    loadingMessage: 'Загрузка данных...',
                    noDataMessage: 'Ошибка при загрузке райнов'
                }, domId);

            this.bindEvents();
        },

        bindEvents: function () {
            this._grid.on('.dgrid-row:dblclick', lang.hitch(this, function (evt) {
                this.zoomToResource(evt);
            }));

        },

        zoomToResource: function(evt) {
            var row = this._grid.row(evt); //row.id == id of group resource

            xhr.get(this._get_extent_url, {
                handleAs: 'json',
                data: {id: row.id}
            }).then(lang.hitch(this, function (data) {
                if (data && data.extent) {
                    topic.publish('map/zoom_to', data.extent);
                }
            }));
        }
    });
});