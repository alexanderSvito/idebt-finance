import urllib

from django.utils import timezone

from idebt.celery import app
from stats.serializers import UserRatingSummarySerializer
from users.models import User
import requests
from django.conf import settings


API_RISK_PATH = '/api/ml/get_risk'


def update_rating(user):
    data = {
        "mths_since_last_delinq": [None, 4.0, 65.0],
        "dti": [12.34, 16.51, 9.03],
        "revol_bal": [15962.0, 8627.0, 16349.0],
        "inq_last_6mths": [0.0, 1.0, 1.0],
        "tot_cur_bal": [91246.0, 35596.0, 622555.0],
        "open_acc": [14.0, 12.0, 28.0],
        "grade": ["B", "B", "A"],
        "tot_coll_amt": [0.0, 0.0, 0.0],
        "sub_grade": ["B2", "B1", "A1"],
        "int_rate": [10.15, 9.67, 6.03],
        "total_acc": [34.0, 22.0, 50.0],
        "earliest_cr_line": ["Jan-1998", "Apr-1998", "Apr-1999"],
        "total_rev_hi_lim": [36100.0, 40700.0, 28600.0],
        "acc_now_delinq": [0.0, 0.0, 0.0],
        "delinq_2yrs": [0.0, 2.0, 0.0],
        "issue_d": ["May-2014", "Jan-2014", "Jul-2014"]
    }
    rating = requests.get(
        urllib.parse.urljoin(
            settings.RISK_PREDICTION_URL,
            API_RISK_PATH
        ),
        data
    ).json()

    user.rating = rating['data'][0]
    user.save()


def collect_summary(user, date=timezone.now().date()):
    summary = {
        "date": date,
        "rating": user.rating,
        "user": user.id,
        "debts_count": len([debt for debt in user.debts.all() if debt.active]),
        "total_debt": round(sum([debt.current_size for debt in user.debts.all() if debt.active]), 2),
        "income": round(sum([credit.current_size for credit in user.credits.all() if credit.active]), 2),
    }
    serializer = UserRatingSummarySerializer(data=summary)
    if serializer.is_valid():
        serializer.save()
    else:
        print(serializer.errors)
        print(serializer.initial_data)


@app.task
def update_users_rating():
    for user in User.objects.all():
        update_rating(user)
        collect_summary(user)
