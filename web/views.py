import json

from django.shortcuts import render, get_object_or_404
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.related import ManyToManyField

from .models import Rin


def to_dict(instance):
    opts = instance._meta
    data = {}
    for f in opts.concrete_fields + opts.many_to_many:
        if isinstance(f, ManyToManyField):
            if instance.pk is None:
                data[f.name] = []
            else:
                data[f.name] = list(f.value_from_object(instance).values_list('pk', flat=True))
        else:
            data[f.name] = f.value_from_object(instance)
    return data


def main_page(request):
    """
    調査結果を記録するページ
    :param request:
    :return:
    """
    context = {
        'records': Rin.objects.all()
    }
    return render(request, 'web/index.html', context)


def insert_record(request):
    """
    postされた情報を記憶する
    :param request:
    :return:
    """
    if request.method == 'POST':
        record = request.POST.get('record')
        # TODO: ここでよしなに分割する
        tree_species = '唐松'
        diameter = 22
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        # latitude = 13.625335
        # longitude = 132.64645

        # save
        r = Rin(tree_species=tree_species, diameter=diameter, latitude=latitude, longitude=longitude)
        r.save()

    context = {
        'records': Rin.objects.all()
    }
    return render(request, 'web/index.html', context)


def statistic_page(request):
    """
    記録した情報を確認、削除できるページ
    :param request:
    :return:
    """
    context = {
        'records': Rin.objects.all()
    }
    return render(request, 'web/statistics.html', context)


def delete_record(request):
    """
    レコードを削除する
    :param request:
    :return:
    """
    record_id = request.GET['id']
    record = get_object_or_404(Rin, pk=record_id)
    record.delete()
    context = {
        'records': Rin.objects.all()
    }
    return render(request, 'web/statistics.html', context)


def map_page(request):
    """
    Mapページ
    :param request:
    :return:
    """
    return render(request, 'web/map.html')


def location_json(request):
    """
    地図情報をjson形式で返す
    :param request:
    :return:
    """
    serialized_queryset = serializers.serialize('json', Rin.objects.all().order_by('created_at'))
    return HttpResponse(serialized_queryset, content_type='application/json')
