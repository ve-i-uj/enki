from .account import Account
from .avatar import Avatar
from .monster import Monster
from .gate import Gate
from .npc import NPC
from . import components

ENTITY_BY_UID = {
    Account.CLS_ID: Account,
    Avatar.CLS_ID: Avatar,
    Monster.CLS_ID: Monster,
    Gate.CLS_ID: Gate,
    NPC.CLS_ID: NPC,

    components.Test.CLS_ID: components.Test,
    components.TestNoBase.CLS_ID: components.TestNoBase,
}
