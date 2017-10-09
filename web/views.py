import re
import requests

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
URL = 'http://52.199.198.108/field_records'


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
            try:
                return data[7]
            except:
                return None
    return None


def extract_digit_words(sentence):
    """
    数字を示す単語を抽出する
    """
    word_first = []
    word_second = []
    word_first_frag = True
    word_second_frag = True
    for morph in default_parser.parse(sentence):
        # 構文解析結果が空であった場合スキップする
        if not morph.surface.strip():
            continue
        data = morph.feature.split(',')
        try:
            if data[7] == 'ニソイチ':
                if word_first_frag:
                    word_first.append('二十一')
                    word_first_frag = False
                elif word_second_frag:
                    word_second.append('二十一')
                    word_second_frag = False
            if data[7] == 'ニジュウサン':
                if word_first_frag:
                    word_first.append('二十三')
                    word_first_frag = False
                elif word_second_frag:
                    word_second.append('二十三')
                    word_second_frag = False
            if data[7] == 'サンジュウサン':
                if word_first_frag:
                    word_first.append('三十三')
                    word_first_frag = False
                elif word_second_frag:
                    word_second.append('三十三')
                    word_second_frag = False
            if data[7] == 'ツチヤ':
                if word_first_frag:
                    word_first.append('二十八')
                    word_first_frag = False
                elif word_second_frag:
                    word_second.append('二十八')
                    word_second_frag = False
        except:
            None
        if data[1] == '数' and word_first_frag:
            word_first.append(morph.surface)
            if len(word_first) >= 1:
                if word_first[0] == '十':
                    if len(word_first) >= 2 and word_first.count('十') == 1:
                        word_first_frag = False

            if len(word_first) >= 2 and word_first.count('十') == 0:
                word_first_frag = False
            elif len(word_first) >= 3 and word_first.count('十') == 1:
                word_first_frag = False

        elif data[1] == '数' and not word_first_frag and word_second_frag:
            word_second.append(morph.surface)
            if len(word_second) > 1:
                if word_second[0] == '十':
                    if len(word_second) >= 2 and word_second.count('十') == 1:
                        word_second_frag = False

            if len(word_second) >= 2 and word_second.count('十') == 0:
                word_second_frag = False
            elif len(word_second) >= 3 and word_second.count('十') == 1:
                word_second_frag = False
    if not word_first or not word_second:
        return None, None
    diameter = kansuji2arabic(''.join(word_first))
    jukou = kansuji2arabic(''.join(word_second))
    return diameter, jukou


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


def check_sentence(request):
    """ 音声認識結果を返す """
    text = request.GET['text']
    diameter, jukou = extract_digit_words(text)
    tree_species = extract_tree_name(text)

    return HttpResponse('{}, 直径: {}, 樹高: {}'.format(tree_species, diameter, jukou))


def extract_digit(words):
    digites = [x for x in re.findall('[0-9]{,2}', words) if x != '']
    return digites[0], digites[1]


def insert_record(request):
    """
    postされた情報を記憶する
    :param request:
    :return:
    """
    if request.method == 'POST':
        record = request.POST.get('record')
        diameter, jukou = extract_digit(record)
        tree_species = extract_tree_name(record)

        if diameter and tree_species:
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')

            # save
            try:
                latitude = float(latitude)
                longitude = float(longitude)
                r = Rin(tree_species=tree_species, diameter=diameter, jukou=jukou, latitude=latitude,
                        longitude=longitude)
                r.save()

                record = {
                    'tyokkei': diameter,
                    'jukou': jukou,
                    'lat': latitude,
                    'lng': longitude
                }
                post_record(record)
            except:
                None
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


def post_record(record):
    """
    取得した内容を指定された場所にPOSTする
    :param record:
    :return:
    """
    context = {
        'field_record[kanriku]': 12,
        'field_record[nendo]': 2017,
        'field_record[rinpan]': 78,
        'field_record[bakku]': '60A1',
        'field_record[shiban]': 1,
        'field_record[shouhan]': 62,
        'field_record[kubun]': 21,
        'field_record[daihyou]': 23,
        'field_record[field_record_details_attributes][0][bangou]': 1,
        'field_record[field_record_details_attributes][0][jushu]': 23,
        'field_record[field_record_details_attributes][0][tyokkei]': record['tyokkei'],
        'field_record[field_record_details_attributes][0][jukou]': record['jukou'],
        'field_record[field_record_details_attributes][0][hini]': 1,
        'field_record[field_record_details_attributes][0][budomari]': 50,
        'field_record[field_record_details_attributes][0][lat]': record['lat'],
        'field_record[field_record_details_attributes][0][lon]': record['lng']
    }
    r = requests.post(URL, context)
    return
