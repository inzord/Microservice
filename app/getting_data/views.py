import zlib
from django.shortcuts import render
import requests
from django.http import HttpResponse
import logging
import time
from datetime import timedelta
import datetime

logging.basicConfig(level='INFO')
logger = logging.getLogger(__name__)
cache = {}


def get_data(request):
    logger.info('get_data start')
    start_time = time.time()

    if request.method == 'GET':
        logger.info('get_data GET start')
        return render(request=request, template_name='getting_data/index.html')

    if request.method == 'POST':
        logger.info('get_data POST start')
        if not request.POST['date']:
            return HttpResponse('Specify the date')
        if cache.get(request.POST['date']):
            context = {
                'list_data': cache.get(request.POST['date']),
                'date': request.POST['date'],
            }
            return render(request=request, template_name='getting_data/index.html',
                          context=context)
        try:

            list_date = request.POST['date'].split() + str(
                datetime.datetime.strptime(request.POST['date'], '%Y-%m-%d').date() - timedelta(days=1)).split()

            response_1st = requests.get('https://www.nbrb.by/api/exrates/rates',
                                        params={'ondate': list_date[0], 'periodicity': '0'})

            response_2st = requests.get('https://www.nbrb.by/api/exrates/rates',
                                        params={'ondate': list_date[1], 'periodicity': '0'})

            response_1st.headers['CRC32'] = str(zlib.crc32(response_1st.request.url.encode('utf-8')))
            response_2st.headers['CRC32'] = str(zlib.crc32(response_2st.request.url.encode('utf-8')))

            response_1st = response_1st.json()
            response_2st = response_2st.json()

            if response_1st:
                cache[list_date[0]] = response_1st
                cache[list_date[1]] = response_2st
                logger.info("get_date Data received ")
                return HttpResponse('Data received')
            else:
                content = 'There is no information from the distant future'
                return HttpResponse(content)
        except Exception as exc:
            logger.error("Server is not active", exc)
        finally:
            finish_time = time.time() - start_time
            logger.info("get_date finished with %.2f sec", finish_time)


def get_by_key(request):
    logger.info('get_by_key start')
    start_time = time.time()

    if request.method == 'POST':
        logger.info('get_by_key POST start')
        return get_data(request)

    if request.method == 'GET':
        logger.info('get_by_key GET start')
        if not request.GET['Cur_Abbreviation']:
            logger.info('get_by_key GET Parameter not specified Cur_Abbreviation')
            return HttpResponse('Parameter not specified Cur_Abbreviation')
        if not request.GET['date']:
            logger.info('get_by_key GET Parameter not specified date')
            return HttpResponse('Parameter not specified date')
        if cache.get(request.GET['date']):
            get_cur_abbreviation_1st = {}
            get_cur_abbreviation_2st = {}
            for item in cache.get(request.GET['date']):
                if item['Cur_Abbreviation'] == request.GET['Cur_Abbreviation']:
                    get_cur_abbreviation_1st = item
                    break
            for item in cache.get(list(cache)[1]):
                if item['Cur_Abbreviation'] == request.GET['Cur_Abbreviation']:
                    get_cur_abbreviation_2st = item
                    break
            value_1st = get_cur_abbreviation_1st['Cur_OfficialRate']
            value_2st = get_cur_abbreviation_2st['Cur_OfficialRate']
            if value_1st > value_2st:
                comparison = "Cur_Abbreviation:{} Дата: {} Ставка={} Выросла по сравнению с Дата: {} Ставка={}".format(
                    request.GET['Cur_Abbreviation'],
                    request.GET['date'], value_1st, list(cache.keys())[1],
                    value_2st)
            elif value_1st < value_2st:
                comparison = "Cur_Abbreviation:{} Дата: {} Ставка={} Уменьшилась по сравнению с Дата: {} Ставка={}".format(
                    request.GET['Cur_Abbreviation'],
                    request.GET['date'], value_1st, list(cache.keys())[1],
                    value_2st)
            else:
                comparison = "Cur_Abbreviation:{} Дата:{} Ставка={} Равна  Дата: {} Ставка={}".format(
                    request.GET['Cur_Abbreviation'],
                    request.GET['date'], value_1st, list(cache.keys())[1],
                    value_2st)
            context = {
                'list_data_1st': get_cur_abbreviation_1st,
                'list_data_2st': get_cur_abbreviation_2st,
                'comparison': comparison,
            }
            finish_time = time.time() - start_time
            logger.info("get_by_key finished with %.2f sec", finish_time)
            return render(request=request, template_name='getting_data/index.html',
                          context=context)
        else:
            content = 'Date not specified'
            finish_time = time.time() - start_time
            logger.info("Date not specified get_by_key finished with  %.2f sec", finish_time)
            return HttpResponse(content)
