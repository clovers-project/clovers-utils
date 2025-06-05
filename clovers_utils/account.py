from datetime import datetime
from typing import Any
from sqlmodel import SQLModel, Field, Relationship
from sqlmodel import Session, create_engine, select
from sqlalchemy import Engine, Column
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON


class BaseItem(SQLModel):
    id: str = Field(primary_key=True)
    name: str


class Exchange(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user: "User" = Relationship(back_populates="exchange")
    user_id: str = Field(foreign_key="user.id")
    stock: "Stock" = Relationship(back_populates="exchange")
    stock_id: str = Field(foreign_key="stock.id")
    #  data
    n: int
    quote: float = 0.0


class Stock(BaseItem, table=True):
    id: str = Field(primary_key=True, foreign_key="group.id")
    group: "Group" = Relationship(back_populates="stock")
    exchange: list[Exchange] = Relationship(back_populates="stock", cascade_delete=True)
    # data
    value: int = 0
    """全群资产"""
    floating: float = 0
    """浮动资产"""
    issuance: int = 0
    """股票发行量"""
    time: float
    """注册时间"""


class AccountBank(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    account: "Account" = Relationship(back_populates="bank")
    account_id: int = Field(foreign_key="account.id")
    # data
    item_id: str = Field(index=True)
    n: int = 0


class Account(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user: "User" = Relationship(back_populates="accounts")
    user_id: str = Field(foreign_key="user.id")
    group: "Group" = Relationship(back_populates="accounts")
    group_id: str = Field(foreign_key="group.id")
    bank: list["AccountBank"] = Relationship(back_populates="account", cascade_delete=True)
    # data
    name: str
    sign_in: datetime | None = None
    extra: dict[str, Any] = Field(default_factory=dict, sa_column=Column(SQLiteJSON()))

    def cancel(self, engine: Engine):
        with Session(engine) as session:
            try:
                account_id = self.id
                if account_id is None:
                    return
                if (account := session.get(Account, account_id)) is None:
                    return
                session.delete(account)
                session.commit()
            except IntegrityError as e:
                session.rollback()
                raise e


class UserBank(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user: "User" = Relationship(back_populates="bank")
    user_id: str = Field(foreign_key="user.id")
    # data
    item_id: str = Field(index=True)
    n: int = 0


class User(BaseItem, table=True):
    accounts: list[Account] = Relationship(back_populates="user", cascade_delete=True)
    bank: list[UserBank] = Relationship(back_populates="user", cascade_delete=True)
    exchange: list[Exchange] = Relationship(back_populates="user", cascade_delete=True)
    # data
    avatar_url: str = ""
    connect: str = ""
    extra: dict[str, Any] = Field(default_factory=dict, sa_column=Column(SQLiteJSON()))
    mailbox: list[str] = Field(default_factory=list, sa_column=Column(SQLiteJSON()))

    def post_message(self, message: str, history: int = 30):
        self.mailbox.append(message)
        self.mailbox = self.mailbox[-history:]

    def cancel(self, engine: Engine):
        with Session(engine) as session:
            try:
                user_id = self.id
                if (user := session.get(User, user_id)) is None:
                    return
                session.delete(user)
                session.commit()
            except IntegrityError as e:
                session.rollback()
                raise e


class GroupBank(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    group: "Group" = Relationship(back_populates="bank")
    group_id: str = Field(foreign_key="group.id")
    # data
    item_id: str = Field(index=True)
    n: int = 0


class Group(BaseItem, table=True):
    accounts: list[Account] = Relationship(back_populates="group", cascade_delete=True)
    bank: list[GroupBank] = Relationship(back_populates="group", cascade_delete=True)
    stock: Stock | None = Relationship(back_populates="group", cascade_delete=True)
    # data
    avatar_url: str = ""
    level: int = 1
    extra: dict[str, Any] = Field(default_factory=dict, sa_column=Column(SQLiteJSON()))

    @property
    def nickname(self):
        return self.stock.name if self.stock is not None else self.name or self.id

    def cancel(self, engine: Engine):
        with Session(engine) as session:
            try:
                group_id = self.id
                if (group := session.get(User, group_id)) is None:
                    return
                session.delete(group)
                session.commit()
            except IntegrityError as e:
                session.rollback()
                raise e


class DataBase:
    def __init__(self, DATABASE_URL: str) -> None:
        self.engine = create_engine(DATABASE_URL)
        SQLModel.metadata.create_all(self.engine)

    @classmethod
    def load(cls, DATABASE_URL: str):
        return cls(DATABASE_URL)

    def user(self, user_id: str, session: Session | None = None):
        with session or Session(self.engine) as session:
            try:
                user = session.get(User, user_id)
                if user is None:
                    user = User(id=user_id, name="")
                    session.add(user)
                    session.commit()
                    session.refresh(user)
                return user
            except IntegrityError as e:
                session.rollback()
                raise e

    def group(self, group_id: str, session: Session | None = None):
        with session or Session(self.engine) as session:
            try:
                group = session.get(Group, group_id)
                if group is None:
                    group = Group(id=group_id, name="")
                    session.add(group)
                    session.commit()
                    session.refresh(group)
                return group
            except IntegrityError as e:
                session.rollback()
                raise e

    def account(self, user_id: str, group_id: str, session: Session | None = None):
        with session or Session(self.engine) as session:
            try:
                query = select(Account).join(User).join(Group).where(User.id == user_id, Group.id == group_id)
                account = session.exec(query).first()
                user = self.user(user_id, session)
                group = self.group(group_id, session)
                if account is None:
                    account = Account(name="", user_id=user.id, group_id=group.id)
                    account.sign_in = datetime.now()
                    session.add(user)
                    session.add(group)
                    session.add(account)
                    session.commit()
                    session.refresh(account)
                return account
            except IntegrityError as e:
                session.rollback()
                raise e

    def save(self, table: SQLModel):
        with Session(self.engine) as session:
            session.add(table)
            session.commit()
            session.refresh(table)

    @property
    def session(self):
        return Session(self.engine)


class Item:
    id: str
    """ID"""
    name: str
    """名称"""
    rare: int
    """稀有度"""
    domain: int
    """
    作用域
        0:无(空气)
        1:群内
        2:全局
    """
    timeliness: int
    """
    时效
        0:时效道具
        1:永久道具
    """
    number: int
    """编号"""
    color: str
    """颜色"""
    intro: str
    """介绍"""
    tip: str
    """提示"""

    def __init__(
        self,
        item_id: str,
        name: str,
        color: str = "black",
        intro: str = "",
        tip: str = "",
    ) -> None:
        if not item_id.startswith("item:") or not item_id.lstrip("item:").isdigit():
            raise ValueError("item_id must be item:digit")
        self.name = name
        self.color = color
        self.intro = intro
        self.tip = tip
        self.id = item_id
        self.rare = int(item_id[5])
        self.domain = int(item_id[6])
        self.timeliness = int(item_id[7])
        self.number = int(item_id[8:])
        if self.domain == 2:
            self.deal = self.deal_with_user
        else:
            self.deal = self.deal_with_account

    @property
    def dict(self):

        return {"item_id": self.id, "name": self.name, "color": self.color, "intro": self.intro, "tip": self.tip}

    def deal(self, session: Session, account: Account, unsettled: int):
        raise NotImplementedError

    @staticmethod
    def deal_with_bank(session: Session, bank: AccountBank | UserBank, unsettled: int):
        if unsettled < 0 and bank.n < (-unsettled):
            return False
        bank.n += unsettled
        session.add(bank)
        session.commit()
        session.refresh(bank)
        return True

    def deal_with_account(self, session: Session, account: Account, unsettled: int):
        account_id = account.id
        if account_id is None:
            return False
        query = select(AccountBank).join(Account).where(Account.id == account_id, AccountBank.item_id == self.id)
        bank = session.exec(query).first() or AccountBank(item_id=self.id, account_id=account_id)
        return self.deal_with_bank(session, bank, unsettled)

    def deal_with_user(self, session: Session, account: Account, unsettled: int):
        user_id = account.user.id
        query = select(UserBank).join(User).where(User.id == user_id, UserBank.item_id == self.id)
        bank = session.exec(query).first() or UserBank(item_id=self.id, user_id=user_id)
        return self.deal_with_bank(session, bank, unsettled)
