import random
import datetime

from finance.models import *
from django.core.management.base import BaseCommand

from finance.serializers import MatchSerializer
from stats.serializers import UserRatingSummarySerializer
from tests.helpers import create_issue, create_offer, get_balance, create_user, get_rating
from users.serializers import UserSerializer
from tests.helpers import get_password


class Command(BaseCommand):
    help = 'Populates the database with seed data'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=100)
        parser.add_argument('--seed', type=int, default=random.randint(0, 10000))
        parser.add_argument('-t', '--truncate', default=True, action='store_false')
        parser.add_argument('-d', '--debts', default=True, action='store_false')

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

    def populate_users(self, num):
        for i in range(num):
            serializer = UserSerializer(data=create_user())
            if serializer.is_valid():
                user = serializer.save()
                user.balance.balance = get_balance(user.rating)
                user.balance.save()
                user.set_password('test')
                user.save()
                self.generate_summaries(user)
                self.stdout.write("User {} {} created".format(
                    user.first_name,
                    user.last_name
                ))
            else:
                self.stderr.write(str(serializer.errors) + str(serializer.initial_data))

    def populate_offers_and_issues(self):
        for user in User.objects.all():
            if user.is_creditor:
                anchor = 1
                while random.random() < anchor:
                    offer = user.offers.create(**create_offer(user))
                    user.balance.balance -= offer.credit_fund
                    user.balance.save()
                    anchor *= 0.7

            anchor = 0.5 if user.is_creditor else 1
            while random.random() < anchor:
                user.issues.create(**create_issue(user))
                anchor *= 0.65

            self.stdout.write("Offers and Issues for {} {} populated".format(
                user.first_name,
                user.last_name
            ))

    def populate_debts(self):
        for offer in Offer.objects.all():
            issues = offer.get_issues()
            self.stdout.write("Inspecting offer {}. Has {} issues available".format(
                offer.id,
                len(issues)
            ))
            for issue in issues:
                if random.random() < 0.7:
                    serializer = MatchSerializer(data={
                        "match_type": Match.OFFER,
                        "from_id": offer.id,
                        "to_id": issue.id
                    })
                    if serializer.is_valid(True):
                        match, matched = serializer.save()
                        if matched:
                            self.stdout.write("Debt created")
        for issue in Issue.objects.all():
            offers = issue.get_offers()
            self.stdout.write("Inspecting issue {}. Has {} offers available".format(
                issue.id,
                len(offers)
            ))
            for offer in offers:
                if random.random() < 0.8:
                    serializer = MatchSerializer(data={
                        "match_type": Match.ISSUE,
                        "from_id": issue.id,
                        "to_id": offer.id
                    })
                    if serializer.is_valid(True):
                        match, matched = serializer.save()
                        if matched:
                            self.stdout.write("Debt created")
                            break

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

        self.populate_users(options['users'])
        self.populate_offers_and_issues()

        if options['debts']:
            self.populate_debts()
