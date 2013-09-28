from django.utils.translation import ugettext as _
from django.utils import formats
from django.core.urlresolvers import reverse
from django import forms
import keops.forms.fields

def get_xtype(field):
    if isinstance(field, forms.DateField):
        return {'xtype': 'datefield', 'baseBodyCls': 'x-form-small-field'}
    elif isinstance(field, forms.DateTimeField):
        return {'xtype': 'datetimefield', 'baseBodyCls': 'x-form-small-field'}
    elif isinstance(field, forms.BooleanField):
        return {'xtype': 'checkbox', 'boxLabel': str(field.label)}
    elif isinstance(field, forms.ModelMultipleChoiceField):
        model = field.queryset.model
        return {
            'xtype': 'itemselector',
            'store': [[r.pk, str(r)] for r in field.queryset],
            'imagePath': '/static/js/extjs/examples/ux/css/images/',
            'msgTarget': 'side',
            'valueField': 'id',
            'displayField': 'text',
            'labelAlign': 'top',
            'labelStyle': 'margin-bottom: 5px',
            'labelSeparator': ':',
            'height': 220,
            'fromTitle': _('Available'),
            'toTitle': _('Selected'),
            'storeUrl': reverse('keops.views.db.lookup'),
            'storeModel': '%s.%s' % (model._meta.app_label, model._meta.model_name)
        }
    elif isinstance(field, forms.ModelChoiceField):
        model = field.queryset.model
        return {
            'xtype': 'keops.combobox',
            'storeUrl': reverse('keops.views.db.lookup'),
            'storeModel': '%s.%s' % (model._meta.app_label, model._meta.model_name)
        }
    elif isinstance(field.widget, forms.widgets.Select):
        return {'xtype': 'combobox', 'store': [[c[0], str(c[1])] for c in field.widget.choices], 'forceSelection': True, 'minChars': 0}
    elif isinstance(field, forms.IntegerField):
        return {'xtype': 'numberfield', 'allowDecimals': False, 'baseBodyCls': 'x-form-small-field'}
    elif isinstance(field, keops.forms.fields.GridField):
        return {'xtype': 'grid'}
    else:
        return {'xtype': 'textfield', 'maxLength': field.widget.attrs.get('maxlength'), 'enforceMaxLength': True}

def grid_column(name, field):
    col = {'header': str(field.label), 'dataIndex': name}
    if isinstance(field, forms.ModelChoiceField) or (isinstance(field, forms.CharField) and int(field.widget.attrs.get('maxlength', 0)) > 30):
        col['width'] = 200
    elif isinstance(field, forms.ChoiceField):
        s = 'switch(value) { %s }' % ''.join(['case "%s": return "%s";' % (c[0], c[1]) for c in field.choices])
        col['renderer'] = 'function (value) { %s }' % s
    elif isinstance(field, forms.NumberInput):
        col['xtype'] = 'numbercolumn'
        col['align'] = 'right'
    elif isinstance(field, forms.IntegerField):
        col['align'] = 'right'
    elif isinstance(field, forms.DateField):
        col['xtype'] = 'datecolumn'
        col['format'] = formats.get_format('SHORT_DATE_FORMAT')
    elif isinstance(field, forms.DateTimeField):
        col['xtype'] = 'datecolumn'
        col['format'] = formats.get_format('SHORT_DATETIME_FORMAT')
    elif isinstance(field, forms.BooleanField):
        col['renderer'] = 'function (value) { if (value === true) return "%s"; else return "%s"; }' % (_('Yes'), _('No'))
    return col

def get_field(name, field):
    d = {'columnWidth': .5, 'fieldLabel': str(field.label), 'name': name, 'labelWidth': 140}
    d.update(get_xtype(field))
    if d['xtype'] == 'checkbox':
        d['labelSeparator'] = ''
        d['fieldLabel'] = ' '
    return d

def get_form_fields(form):
    for k, v in form.widgets.items():
        yield k, get_field(v)

def get_container(container):
    items = [get_field(*f) for f in container]
    items[0]['padding'] =  '2 0 2 0'
    for i in items[1:]:
        i['padding'] =  '2 0 2 8'
    d = {'columnWidth': .5, 'xtype': 'fieldcontainer', 'layout': 'hbox', 'padding': '3 8 6 0', 'items': items}
    return d

def get_form_items(form):
    items = []
    pages = []
    for page in form:
        if page.name:
            fieldsets = []
            fsets = {
                'xtype': 'panel',
                'title': str(page.name),
                'items': fieldsets,
                'layout': 'column',
                'defaults': { 'padding': "5 8 8 8" }
            }
            pages.append(fsets)
        else:
            fieldsets = items
        for fieldset in page:
            if fieldset.name:
                fields = []
                fs = {'xtype': 'fieldset', 'title': str(fieldset.name), 'items': fields}
                fieldsets.append(fs)
            else:
                fields = fieldsets

            for container in fieldset:
                container = [f for f in container]
                if len(container) == 1:
                    fields.append(get_field(*container[0]))
                else:
                    fields.append(get_container(container))
    if pages:
        tabpage = {'xtype': 'tabpanel', 'columnWidth': 1, 'items': pages, 'frame': True, 'padding': '0 0 0 0'}
        items.append(tabpage)
    return items