from django.conf import settings

def misc(request):
    return { 'LOCAL_DEV': settings.LOCAL_DEV, 'POLICITIAN_TYPE': settings.POLITICIAN_NAME }