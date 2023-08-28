import typing
from typing import Type
from unittest import TestCase

from enki.core import msgspec, utils
from enki.core.kbeenum import ComponentType
from enki.handler import serverhandler
from enki.handler.serverhandler.loginapphandler import OnBaseappInitProgressHandler, \
    OnDbmgrInitCompletedHandler, OnAppActiveTickHandler
from tools import msgreader


class OnDbmgrInitCompletedTestCase(TestCase):

    def test_onDbmgrInitCompleted(self):
        handlers = serverhandler.SERVER_HANDLERS.get('loginapp')
        assert handlers is not None
        handler_cls = handlers.get(
            msgspec.app.loginapp.onDbmgrInitCompleted.id
        )
        assert handler_cls is not None
        handler_cls = typing.cast(Type[OnDbmgrInitCompletedHandler], handler_cls)

        str_data = '0e0029000500000001000000303645313546313032423438314143463843413139453246343130443142363400'
        data = msgreader.normalize_wireshark_data(str_data)
        serializer = utils.get_serializer_for(ComponentType.LOGINAPP)
        msg, data_tail = serializer.deserialize(memoryview(data))
        assert not data_tail
        assert msg is not None

        res = handler_cls().handle(msg)
        assert res.success
        pd = res.result

        assert pd.startID == 1
        assert pd.endID == 826619440
        assert pd.startGlobalOrder == 808535605
        assert pd.startGroupOrder == 942948914
        assert pd.digest == '1ACF8CA19E2F410D1B64'


class OnBaseappInitProgressTestCase(TestCase):

    def test_OnBaseappInitProgressHandler(self):
        handlers = serverhandler.SERVER_HANDLERS.get('loginapp')
        assert handlers is not None
        handler_cls = handlers.get(
            msgspec.app.loginapp.onBaseappInitProgress.id
        )
        assert handler_cls is not None
        handler_cls = typing.cast(Type[OnBaseappInitProgressHandler], handler_cls)

        str_data = '18000000c842'
        data = msgreader.normalize_wireshark_data(str_data)
        serializer = utils.get_serializer_for(ComponentType.LOGINAPP)
        msg, data_tail = serializer.deserialize(memoryview(data))
        assert not data_tail
        assert msg is not None

        res = handler_cls().handle(msg)
        assert res.success
        pd = res.result

        assert pd.progress == 100.0


class OnAppActiveTickTestCase(TestCase):

    def test_OnAppActiveTickHandler(self):
        handlers = serverhandler.SERVER_HANDLERS.get('loginapp')
        assert handlers is not None
        handler_cls = handlers.get(
            msgspec.app.loginapp.onAppActiveTick.id
        )
        assert handler_cls is not None
        handler_cls = typing.cast(Type[OnAppActiveTickHandler], handler_cls)

        str_data = '42d70a000000d107000000000000'
        data = msgreader.normalize_wireshark_data(str_data)
        serializer = utils.get_serializer_for(ComponentType.LOGINAPP)
        msg, data_tail = serializer.deserialize(memoryview(data))
        assert not data_tail
        assert msg is not None

        res = handler_cls().handle(msg)
        assert res.success
        pd = res.result

        assert pd.componentType == 10
        assert pd.componentID == 2001
