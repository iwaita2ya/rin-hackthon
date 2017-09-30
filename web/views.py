import re

from django.shortcuts import render, get_object_or_404
from django.core import serializers
from django.http import HttpResponse

from .parser import default_parser

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


def extract_tree_name(sentence):
    """文から樹木種を抽出する"""
    for morph in default_parser.parse(sentence):
        # 構文解析結果が空であった場合スキップする
        if not morph.surface.strip():
            continue
        data = morph.feature.split(',')
        if data[0] == '名詞' and data[1] in ('一般', '固有名詞'):
            return data[7]
    return None


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


def extract_tree_diameter(text):
    text = kansuji2arabic(text)
    try:
        diameter = int(''.join(re.findall('[0-9]', text)))
        return diameter
    except:
        return None


def check_sentence(request):
    """ 音声認識結果を返す """
    text = request.GET['text']
    diameter = extract_tree_diameter(text)
    tree_species = extract_tree_name(text)

    return HttpResponse('{}, {}'.format(tree_species, diameter))


def insert_record(request):
    """
    postされた情報を記憶する
    :param request:
    :return:
    """
    if request.method == 'POST':
        record = request.POST.get('record')
        diameter = extract_tree_diameter(record)
        tree_species = extract_tree_name(record)

        if diameter and tree_species:
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')

            if latitude and longitude:
                # save
                r = Rin(tree_species=tree_species, diameter=diameter, latitude=latitude, longitude=longitude)
                r.save()

    context = {
        'records': Rin.objects.all().order_by('-created_at')[:7]
    }
    return render(request, 'web/index.html', context)


def statistic_page(request):
    """
    記録した情報を確認、削除できるページ
    :param request:
    :return:
    """
    context = {
        'records': Rin.objects.all().order_by('-created_at')[:7]
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
        'records': Rin.objects.all().order_by('-created_at')[:7]
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
    serialized_queryset = serializers.serialize('json', Rin.objects.all().order_by('-created_at')[:7])
    return HttpResponse(serialized_queryset, content_type='application/json')
