import random
import datetime

from finance.models import *
from django.core.management.base import BaseCommand

from finance.serializers import MatchSerializer
from stats.serializers import UserRatingSummarySerializer
from stats.tasks import collect_summary
from tests.helpers import create_issue, create_offer, get_balance, create_user, get_rating
from users.serializers import UserSerializer

from django.core.management import call_command


class Command(BaseCommand):
    help = 'Populates the database with seed data'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=100)
        parser.add_argument('--seed', type=int, default=random.randint(0, 10000))
        parser.add_argument('-t', '--truncate', default=True, action='store_false')
        parser.add_argument('-d', '--debts', default=True, action='store_false')
        parser.add_argument('-i', '--interactive', default=False, action='store_true')
        parser.add_argument('--days', type=int, default=31)

    def get_time_series(self, start, end):
        dt = start
        step = datetime.timedelta(hours=24)

        result = []

        while dt < end:
            result.append(dt.date())
            dt += step

        return result

    def generate_summaries(self, user):
        days_in_system = random.randint(7, 100)
        start_date = datetime.datetime.now() - datetime.timedelta(hours=24 * days_in_system)
        for date in self.get_time_series(start_date, datetime.datetime.now()):
            rating = get_rating()
            summary = {
                "date": date,
                "rating": get_rating(),
                "user": user.id,
                "debts_count": random.randint(0, 4),
                "total_debt": round(random.random() * rating * rating, 2),
                "income": round(random.random() * rating * rating, 2)
            }
            serializer = UserRatingSummarySerializer(data=summary)
            serializer.is_valid(raise_exception=True)
            serializer.save()

    def populate_users(self, num, date=timezone.now()):
        for i in range(num):
            user_data = create_user()
            user_data['date_joined'] = datetime.datetime.combine(date, datetime.datetime.min.time())
            serializer = UserSerializer(data=user_data)
            if serializer.is_valid():
                user = serializer.save()
                user.balance.balance = get_balance(user.rating)
                user.balance.save()
                user.set_password('test')
                user.save()
                # self.generate_summaries(user)
                self.stdout.write("User {} {} created".format(
                    user.first_name,
                    user.last_name
                ))
            else:
                self.stderr.write(str(serializer.errors) + str(serializer.initial_data))

    def populate_offers_and_issues(self, date=timezone.now().date()):
        for user in User.objects.all():
            if user.is_creditor:
                anchor = 1 if len(user.offers.all()) == 0 else 0.2
                while random.random() < anchor:
                    offer_data = create_offer(user)
                    offer_data['created_at'] = date
                    offer = user.offers.create(**offer_data)
                    user.balance.balance -= offer.credit_fund
                    user.balance.save()
                    anchor *= 0.8

            if user.is_creditor and len(user.issues.all()) == 0:
                anchor = 0.5
            elif len(user.issues.all()) == 0:
                anchor = 1
            else:
                anchor = 0.3
            while random.random() < anchor:
                issue_data = create_issue(user)
                issue_data['created_at'] = date
                user.issues.create(**issue_data)
                anchor *= 0.85

            self.stdout.write("Offers and Issues for {} {} populated".format(
                user.first_name,
                user.last_name
            ))

    def populate_debts(self, date=timezone.now().date()):
        for offer in Offer.objects.filter(is_closed=False):
            if not offer.dried:
                issues = offer.get_issues()
                self.stdout.write("Inspecting offer {}. Has {} issues available".format(
                    offer.id,
                    len(issues)
                ))
                for issue in issues:
                    if random.random() < 0.8:
                        serializer = MatchSerializer(data={
                            "match_type": Match.OFFER,
                            "from_id": offer.id,
                            "to_id": issue.id
                        })
                        if serializer.is_valid(True):
                            match, matched = serializer.save()
                            if matched:
                                self.stdout.write("Debt created")
                                issue.investment.created_at = date
                                issue.investment.save()
        for issue in Issue.objects.filter(is_closed=False, fulfilled=False):
            offers = issue.get_offers()
            self.stdout.write("Inspecting issue {}. Has {} offers available".format(
                issue.id,
                len(offers)
            ))
            for offer in offers:
                if random.random() < 0.9:
                    serializer = MatchSerializer(data={
                        "match_type": Match.ISSUE,
                        "from_id": issue.id,
                        "to_id": offer.id
                    })
                    if serializer.is_valid(True):
                        match, matched = serializer.save()
                        if matched:
                            self.stdout.write("Debt created")
                            issue.investment.created_at = date
                            issue.investment.save()
                            break

    def decide_to_repay(self, user, debt, date):
        return (user.balance.balance >= debt.current_size
                and (date - debt.created_at).days > debt.issue.min_credit_period
                and random.random() < 0.9
                )

    def replay_debts(self, date):
        for user in User.objects.all():
            for debt in user.debts.all():
                if self.decide_to_repay(user, debt, date):
                    debt.repay_funds(date)

    def process_users(self, date):
        arrived = int(abs(random.gauss(3, 5)))
        self.populate_users(arrived)
        for user in User.objects.all():
            anchor = random.random()
            if anchor < 0.4:
                user.replenish(random.randint(10, 1500))
            elif anchor < 0.6:
                balance = int(user.balance.balance)
                if balance > 0:
                    user.withdraw(random.randint(0, balance))
            else:
                pass

    def get_statistics(self, date):
        for user in User.objects.all():
            if len(user.debts.all()) != 0:
                user.rating -= int(len(user.debts.all()) / 2)
            else:
                user.rating += random.randint(0, 100 - user.rating)
            user.save()
            collect_summary(user, date)

    def imitate(self, num,  days):
        start_date = datetime.datetime.now() - datetime.timedelta(hours=24 * days)
        self.populate_users(num, start_date)
        for date in self.get_time_series(start_date, datetime.datetime.now()):
            self.stderr.write("Day: " + date.strftime("%Y-%m-%d"))
            self.process_users(date)
            self.populate_offers_and_issues(date)
            self.populate_debts(date)
            self.replay_debts(date)
            self.get_statistics(date)

    def handle(self, *args, **options):
        random.seed(options['seed'])
        if options['truncate']:
            User.objects.all().delete()
            self.stdout.write("All users deleted")
            Offer.objects.all().delete()
            self.stdout.write("All offers deleted")
            Issue.objects.all().delete()
            self.stdout.write("All issues deleted")
            Debt.objects.all().delete()
            self.stdout.write("All debts deleted")
        call_command('create_system')
        if options['interactive']:
            self.imitate(options['users'], options['days'])
        else:
            self.populate_users(options['users'])
            self.populate_offers_and_issues()

            if options['debts']:
                self.populate_debts()
