import attr
from django.db.models import Exists, F, Value, OuterRef, CharField
from django.db.models.functions import Concat

from authentication.models import CustomUser
from tests.models import Attempt, Test


@attr.s
class ResultsFactory:
    user_id = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(int))
    )
    test_id = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(int))
    )

    def __get_for_user(self):
        attempts_qs = Attempt.objects.filter(
            user_id=self.user_id,
            test_id=OuterRef('id'),
            result__gte=OuterRef('min_result')
        )
        tests_qs = Test.objects.filter(is_visible=True) \
            .order_by('title').values('title', is_success=Exists(attempts_qs))
        return list(tests_qs)

    def __get_for_test(self):
        min_result = Test.objects.values('min_result')\
            .get(id=self.test_id)['min_rezult']
        attempts_qs = Attempt.objects.filter(
            user_id=OuterRef('id'),
            test_id=self.test_id,
            result__gte=min_result
        )
        users_qs = CustomUser.objects.filter(role='user').values(
            user=Concat(
                F('last_name'),
                Value(' ', CharField()),
                F('first_name')
            ),
            is_success=Exists(attempts_qs)
        ).order_by('user')
        return list(users_qs)

    def __get_for_user_by_test(self):
        attempts_qs = Attempt.objects.filter(
            user_id=self.user_id,
            test_id=self.test_id,
            result__gte=OuterRef('min_result')
        )
        test = Test.objects.values(
            'title',
            is_success=Exists(attempts_qs)
        ).get(id=self.test_id)
        return dict(test)

    @property
    def data(self):
        if self.user_id and self.test_id:
            return self.__get_for_user_by_test()
        if self.test_id:
            return self.__get_for_test()
        return self.__get_for_user()
