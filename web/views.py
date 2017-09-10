import re

from django.shortcuts import render, get_object_or_404
from django.core import serializers
from django.http import HttpResponse
from django.db.models.fields.related import ManyToManyField

from .models import Rin

tt_ksuji = str.maketrans('一二三四五六七八九〇壱弐参', '1234567890123')

re_suji = re.compile(r'[十拾百千万億兆\d]+')
re_kunit = re.compile(r'[十拾百千]|\d+')
re_manshin = re.compile(r'[万億兆]|[^万億兆]+')

TRANSUNIT = {'十': 10,
             '拾': 10,
             '百': 100,
             '千': 1000}
TRANSMANS = {'万': 10000,
             '億': 100000000,
             '兆': 1000000000000}


def kansuji2arabic(kstring, sep=False):
    """漢数字をアラビア数字に変換"""

    def _transvalue(sj, re_obj=re_kunit, transdic=TRANSUNIT):
        unit = 1
        result = 0
        for piece in reversed(re_obj.findall(sj)):
            if piece in transdic:
                if unit > 1:
                    result += unit
                unit = transdic[piece]
            else:
                val = int(piece) if piece.isdecimal() else _transvalue(piece)
                result += val * unit
                unit = 1

        if unit > 1:
            result += unit

        return result

    transuji = kstring.translate(tt_ksuji)
    for suji in sorted(set(re_suji.findall(transuji)), key=lambda s: len(s),
                           reverse=True):
        if not suji.isdecimal():
            arabic = _transvalue(suji, re_manshin, TRANSMANS)
            arabic = '{:,}'.format(arabic) if sep else str(arabic)
            transuji = transuji.replace(suji, arabic)

    return transuji


def main_page(request):
    """
    調査結果を記録するページ
    :param request:
    :return:
    """
    context = {
        'records': Rin.objects.all().order_by('-created_at')
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
        record = kansuji2arabic(record)
        try:
            diameter = int(''.join(re.findall('[0-9]', record)))
        except:
            diameter = 22
        tree_species = '唐松'
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        # latitude = 13.625335
        # longitude = 132.64645

        # save
        r = Rin(tree_species=tree_species, diameter=diameter, latitude=latitude, longitude=longitude)
        r.save()

    context = {
        'records': Rin.objects.all().order_by('-created_at')
    }
    return render(request, 'web/index.html', context)


def statistic_page(request):
    """
    記録した情報を確認、削除できるページ
    :param request:
    :return:
    """
    context = {
        'records': Rin.objects.all().order_by('-created_at')
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
    serialized_queryset = serializers.serialize('json', Rin.objects.all().order_by('-created_at'))
    return HttpResponse(serialized_queryset, content_type='application/json')
