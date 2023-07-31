# coding=utf-8

from uuid import NAMESPACE_URL, UUID, uuid5

from eventsourcing.application import AggregateNotFound, Application

from banking.domainmodel import Account, BadCredentials, UserAggregate
from uuid import UUID
from decimal import Decimal
from banking.domainmodel import BankAccount


class UserApplication(Application):
    def get_user(self, user_id):
        user = self.repository.get(user_id)
        return user

    def add_user(self, params):
        user = UserAggregate(**params)
        self.save(user)
        return user.id

    def change_password(self, user_id, password):
        try:
            user = self.repository.get(user_id)
            user.change_password(password)
            self.save(user)
        except AggregateNotFound:
            raise UserNotFoundError(user_id)


class Bank(Application):
    """
    This is the model of the application, it has
    all of its events in the from of aggregate
    events that it loads. This loads and
    saves aggregates and forms the business logic
    for reading and writing.

    To create an aggregate run:
      new_account = Account(...)

    To load existing aggregates run:
      account1 = self.repository.get(account_id1)
      account2 = self.repository.get(account_id2)

    To save any aggregates run:
      self.save(account1, account2, new_account)
    """

    def open_account(self, full_name: str, email_address: str) -> UUID:
        account = BankAccount.open(
            full_name=full_name,
            email_address=email_address,
        )
        self.save(account)
        return account.id

    def get_account(self, account_id: UUID) -> BankAccount:
        try:
            aggregate = self.repository.get(account_id)
        except AggregateNotFound:
            raise AccountNotFoundError(account_id)
        else:
            assert isinstance(aggregate, BankAccount)
            return aggregate

    def get_balance(self, account_id: UUID) -> Decimal:
        account = self.get_account(account_id)
        return account.balance

    def deposit_funds(self, credit_account_id: UUID, amount: Decimal) -> None:
        account = self.get_account(credit_account_id)
        account.append_transaction(amount)
        self.save(account)

    def withdraw_funds(self, debit_account_id: UUID, amount: Decimal) -> None:
        account = self.get_account(debit_account_id)
        account.append_transaction(-amount)
        self.save(account)

    def transfer_funds(
        self,
        debit_account_id: UUID,
        credit_account_id: UUID,
        amount: Decimal,
    ) -> None:
        debit_account = self.get_account(debit_account_id)
        credit_account = self.get_account(credit_account_id)
        debit_account.append_transaction(-amount)
        credit_account.append_transaction(amount)
        self.save(debit_account, credit_account)

    def set_overdraft_limit(self, account_id: UUID, overdraft_limit: Decimal) -> None:
        account = self.get_account(account_id)
        account.set_overdraft_limit(overdraft_limit)
        self.save(account)

    def get_overdraft_limit(self, account_id: UUID) -> Decimal:
        account = self.get_account(account_id)
        return account.overdraft_limit

    def close_account(self, account_id: UUID) -> None:
        account = self.get_account(account_id)
        account.close()
        self.save(account)


class AccountNotFoundError(Exception):
    pass


class UserNotFoundError(Exception):
    pass
