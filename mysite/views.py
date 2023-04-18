import datetime
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.core.cache import cache
from read_statistics.utils import get_seven_days_read_data, get_today_hot_date, get_yesterday_hot_date
from blog.models import Blog
from django.db.models import Sum


def get_7_days_hot_blogs():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects\
        .filter(read_details__date__lte=today, read_details__date__gte=date)\
        .values('id', 'title')\
        .annotate(read_num_sum=Sum('read_details__read_num'))\
        .order_by('-read_num_sum')
    return blogs[:3]


def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    read_nums, dates = get_seven_days_read_data(blog_content_type)
    today_hot_data = get_today_hot_date(blog_content_type)
    yesterday_hot_data = get_yesterday_hot_date(blog_content_type)

    # 获取7天热门博客的缓存数据
    days_7_hot_data = cache.get('days_7_hot_data')
    if days_7_hot_data is None:
        days_7_hot_data = get_7_days_hot_blogs()
        cache.set('days_7_hot_data', days_7_hot_data, 3600)
        print('cacl')
    else:
        print('use caches')



    context = {}
    context['read_nums'] = read_nums
    context['dates'] = dates
    context['today_hot_data'] = today_hot_data
    context['yesterday_hot_data'] = yesterday_hot_data
    context['days_7_hot_data'] = days_7_hot_data
    return render(request, 'home.html', context)


