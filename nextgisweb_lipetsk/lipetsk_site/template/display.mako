<%inherit file='nextgisweb:pyramid/template/base.mako' />

<%def name="head()">
    <% import json %>

    <script type="text/javascript">
        var displayConfig = ${json.dumps(display_config, indent=4).replace('\n', '\n' + (8 * ' ')) | n};

        require([
            "dojo/parser",
            "dojo/ready",
            "ngw-lipetsk-site/Display"
        ], function (
            parser,
            ready
        ) {
            ready(function() {
                parser.parse();
            });
        });
    </script>

    <style type="text/css">
        body, html { width: 100%; height: 100%; margin:0; padding: 0; overflow: hidden; }
    </style>

</%def>

<div style="width: 100%; background: url(${request.static_url('nextgisweb_lipetsk:lipetsk_site/static/background.svg')});">
    <img style="z-index: 5; padding: 5px 5px; position: relative" src="${request.static_url('nextgisweb_lipetsk:lipetsk_site/static/logo.png')}" alt="ГИС ЭКОЛОГИИ ЛИПЕЦКОЙ ОБЛАСТИ">
    <div style="z-index: 1; height: 92px; width: 400px; top: 0;position: absolute; background: url(${request.static_url('nextgisweb_lipetsk:lipetsk_site/static/flag.png')}) no-repeat scroll 0 0;"></div>
</div>

<div data-dojo-id="display"
    data-dojo-type="ngw-lipetsk-site/Display"
    data-dojo-props="config: displayConfig"
    style="width: 100%; height: 100%">
</div>
