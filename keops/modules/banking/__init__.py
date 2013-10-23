from django.utils.translation import ugettext_lazy as _

app_info = {
    'name': 'Banking',
    'description': _('Basic banking module.'),
    'category': _('Banking'),
    'version': '0.1',
    'dependencies': ['keops.modules.base']
}
