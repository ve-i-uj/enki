import unittest

from enki.app import handler, appl
from enki import settings
from enki.net import kbeclient, msgspec

from enki.app import ehelper
from enki.interface import IMessage, IMsgReceiver

from tests.utests.base import EnkiBaseTestCase


class OnUpdateBasePosTestCase(EnkiBaseTestCase):
    """Test onUpdateBasePos"""

    def test_ok(self):
        data = b'\xf8\x01\x14\x00\x00\x00\x07\x00\x95\x84\xfbb\x81\x08\x00\x00Account\x00'
        msg_504, _ = kbeclient.MessageSerializer().deserialize(memoryview(data))
        assert msg_504 is not None
        res_504 = handler.OnCreatedProxiesHandler(self._entity_helper).handle(msg_504)
        assert res_504.success

        data = b'\r\x00\x00\x14\x9aQD\xdd\x8eCD\xaf\x99\x91\xbf\x18\x00\t\x00\x00\t}QDM\x9cCD\x18\x00\t\x00\x00\xfe_QD\xbc\xa9CD\x18\x00\t\x00\x00\xf3BQD,\xb7CD\x18\x00\t\x00\x00\xe8%QD\x9b\xc4CD\x18\x00\t\x00\x00\xdd\x08QD\x0b\xd2CD\x18\x00\t\x00\x00\xd2\xebPDz\xdfCD\x18\x00\t\x00\x00\xc7\xcePD\xea\xecCD\x18\x00\t\x00\x00\xbc\xb1PDZ\xfaCD\x18\x00\t\x00\x00\xb1\x94PD\xc9\x07DD\x18\x00\t\x00\x00\xa6wPD9\x15DD\x18\x00\t\x00\x00\x9bZPD\xa8"DD\x18\x00\t\x00\x00\x90=PD\x180DD\x18\x00\t\x00\x00\x85 PD\x87=DD\x18\x00\t\x00\x00z\x03PD\xf7JDD\x18\x00\t\x00\x00o\xe6ODfXDD\x18\x00\t\x00\x00d\xc9OD\xd6eDD\x18\x00\t\x00\x00Y\xacODEsDD\x18\x00\t\x00\x00N\x8fOD\xb5\x80DD\x18\x00\t\x00\x00CrOD$\x8eDD\x18\x00\t\x00\x008UOD\x94\x9bDD\x18\x00\t\x00\x00-8OD\x03\xa9DD\x18\x00\t\x00\x00"\x1bODs\xb6DD\x18\x00\t\x00\x00\x17\xfeND\xe2\xc3DD\x18\x00\t\x00\x00\x0c\xe1NDR\xd1DD\x18\x00\t\x00\x00\x01\xc4ND\xc1\xdeDD\x18\x00\t\x00\x00\xf6\xa6ND1\xecDD\x18\x00\t\x00\x00\xeb\x89ND\xa0\xf9DD\x18\x00\t\x00\x00\xe0lND\x10\x07ED\x18\x00\t\x00\x00\xd5OND\x7f\x14ED\x18\x00\t\x00\x00\xca2ND\xef!ED\x18\x00\t\x00\x00\xbf\x15ND^/ED\x18\x00\t\x00\x00\xb4\xf8MD\xce<ED\x18\x00\t\x00\x00\xa9\xdbMD=JED\x18\x00\t\x00\x00\x9e\xbeMD\xadWED\x18\x00\t\x00\x00\x93\xa1MD\x1ceED\x18\x00\t\x00\x00\x88\x84MD\x8crED\x18\x00\t\x00\x00}gMD\xfc\x7fED\x18\x00\t\x00\x00rJMDk\x8dED\x18\x00\t\x00\x00g-MD\xdb\x9aED\x18\x00\t\x00\x00\\\x10MDJ\xa8ED\x18\x00\t\x00\x00Q\xf3LD\xba\xb5ED\x18\x00\t\x00\x00F\xd6LD)\xc3ED\x18\x00\t\x00\x00;\xb9LD\x99\xd0ED\x18\x00\t\x00\x000\x9cLD\x08\xdeED\x18\x00\t\x00\x00%\x7fLDx\xebED\x18\x00\t\x00\x00\x1abLD\xe7\xf8ED\x18\x00\t\x00\x00\x0fELDW\x06FD\x18\x00\t\x00\x00\x04(LD\xc6\x13FD\x18\x00\t\x00\x00\xf9\nLD6!FD\x18\x00\t\x00\x00\xee\xedKD\xa5.FD\x18\x00\t\x00\x00\xe3\xd0KD\x15<FD\x18\x00\t\x00\x00\xd8\xb3KD\x84IFD\x18\x00\t\x00\x00\xcd\x96KD\xf4VFD\x18\x00\t\x00\x00\xc2yKDcdFD\x18\x00\t\x00\x00\xb7\\KD\xd3qFD\x18\x00\t\x00\x00\xac?KDB\x7fFD\x18\x00\t\x00\x00\xa1"KD\xb2\x8cFD\x18\x00\t\x00\x00\x96\x05KD!\x9aFD\x18\x00\t\x00\x00\x8b\xe8JD\x91\xa7FD\x18\x00\t\x00\x00\x80\xcbJD\x00\xb5FD\x18\x00\t\x00\x00u\xaeJDp\xc2FD\x18\x00\t\x00\x00j\x91JD\xdf\xcfFD\x18\x00\t\x00\x00_tJDO\xddFD\x18\x00\t\x00\x00TWJD\xbe\xeaFD\x18\x00\t\x00\x00I:JD.\xf8FD\x18\x00\t\x00\x00>\x1dJD\x9d\x05GD\x18\x00\t\x00\x003\x00JD\r\x13GD\x18\x00\t\x00\x00(\xe3ID| GD\x18\x00\t\x00\x00\x1d\xc6ID\xec-GD\x18\x00\t\x00\x00\x12\xa9ID\\;GD\x18\x00\t\x00\x00\x07\x8cID\xcbHGD\x18\x00\t\x00\x00\xfcnID;VGD\x18\x00\t\x00\x00\xf1QID\xaacGD\x18\x00\t\x00\x00\xe64ID\x1aqGD\x18\x00\t\x00\x00\xdb\x17ID\x89~GD\x18\x00\t\x00\x00\xd0\xfaHD\xf9\x8bGD\x18\x00\t\x00\x00\xc5\xddHDh\x99GD\x18\x00\t\x00\x00\xba\xc0HD\xd8\xa6GD\x18\x00\t\x00\x00\xaf\xa3HDG\xb4GD\x18\x00\t\x00\x00\xa4\x86HD\xb7\xc1GD\x18\x00\t\x00\x00\x99iHD&\xcfGD\x18\x00\t\x00\x00\x8eLHD\x96\xdcGD\x18\x00\t\x00\x00\x83/HD\x05\xeaGD\x18\x00\t\x00\x00x\x12HDu\xf7GD\x18\x00\t\x00\x00\x00\x00HD\x00\x00HD\x1d\x00\r\x00\x00Z\xe9GD\x9b\x16HD\xfcNI\xbf\x1d\x00\r\x00\x00\xb4\xd2GD6-HD\xfcNI\xbf\x18\x00\t\x00\x00\x0e\xbcGD\xd1CHD\x18\x00\t\x00\x00h\xa5GDlZHD\x18\x00\t\x00\x00\xc2\x8eGD\x07qHD\x18\x00\t\x00\x00\x1cxGD\xa2\x87HD\x18\x00\t\x00\x00uaGD=\x9eHD\x18\x00\t\x00\x00\x94YGD\x1a\xa6HD\x18\x00\t\x00\x00\x94YGD\x1a\xa6HD\x1d\x00\r\x00\x00YiGDB\x8aHD\xb9\x14(@\r\x00\x81\xe5@D\x83\x00SC3#BD\xff\x01t\x00\xd4\x07\x00\x00\x00\x01*\xd4QD|2SC\xfdsCD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00}5\xfc?\x00\x04d\x00\x00\x00\x00\x05d\x00\x00\x00\x00\x06d\x00\x00\x00\x00\x07d\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\n\xe901\x01\x00\x0b\n\x00\x0c2\x00\r\x0c\x00\x00\x00\xe8\x89\xbe\xe5\x85\x8b\xe6\x96\xaf\xe7\x90\x83\x00\x0e\x00\x00\x0f\x00\x00\x10\xe901\x01\x00\x11\x01\x00\x00\x00\xfb\x01\x05\x00\xd4\x07\x00\x00\x05\xff\x01S\x00\xd1\x07\x00\x00\x00\x01\x8e\x01DDM\xf3RCq\x91CD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\xa0\xc40\xc0\x00\x04\x00\x00\x00\x00\x00\x05i\x9a\x98\x00\x00\x06\x0f\x00\x072\x00\x08\x0f\x00\x00\x00\xe6\x96\xb0\xe6\x89\x8b\xe6\x8e\xa5\xe5\xbe\x85\xe5\x91\x98\x00\ti\x9a\x98\x00\x00\n\x01\x00\x00\x00\xfb\x01\x06\x00\xd1\x07\x00\x00\x06\x00\x1d\x00\r\x00\x00\x1f\xb7QDm\x81CD\xaf\x99\x91\xbf\x1d\x00\r\x00\x00\x14\x9aQD\xdd\x8eCD\xaf\x99\x91\xbf\x18\x00\t\x00\x00\t}QDM\x9cCD\x18\x00\t\x00\x00\xfe_QD\xbc\xa9CD\x18\x00\t\x00\x00\xf3BQD,\xb7CD\x18\x00\t\x00\x00\xe8%QD\x9b\xc4CD\x18\x00\t\x00\x00\xdd\x08QD\x0b\xd2CD\x18\x00\t\x00\x00\xd2\xebPDz\xdfCD\x18\x00\t\x00\x00\xc7\xcePD\xea\xecCD\x18\x00\t\x00\x00\xbc\xb1PDZ\xfaCD\x18\x00\t\x00\x00\xb1\x94PD\xc9\x07DD\x18\x00\t\x00\x00\xa6wPD9\x15DD\x18\x00\t\x00\x00\x9bZPD\xa8"DD\x18\x00\t\x00\x00\x90=PD\x180DD\x18\x00\t\x00\x00\x85 PD\x87=DD\x18\x00\t\x00\x00z\x03PD\xf7JDD\x18\x00\t\x00\x00o\xe6ODfXDD\x18\x00\t\x00\x00d\xc9OD\xd6eDD\x18\x00\t\x00\x00Y\xacODEsDD\x18\x00\t\x00\x00N\x8fOD\xb5\x80DD\x18\x00\t\x00\x00CrOD$\x8eDD\x18\x00\t\x00\x008UOD\x94\x9bDD\x18\x00\t\x00\x00-8OD\x03\xa9DD\x18\x00\t\x00\x00"\x1bODs\xb6DD\x18\x00\t\x00\x00\x17\xfeND\xe2\xc3DD\x18\x00\t\x00\x00\x0c\xe1NDR\xd1DD\x18\x00\t\x00\x00\x01\xc4ND\xc1\xdeDD\x18\x00\t\x00\x00\xf6\xa6ND1\xecDD\x18\x00\t\x00\x00\xeb\x89ND\xa0\xf9DD\x18\x00\t\x00\x00\xe0lND\x10\x07ED\x18\x00\t\x00\x00\xd5OND\x7f\x14ED\x18\x00\t\x00\x00\xca2ND\xef!ED\x18\x00\t\x00\x00\xbf\x15ND^/ED\x18\x00\t\x00\x00\xb4\xf8MD\xce<ED\x18\x00\t\x00\x00\xa9\xdbMD=JED\x18\x00\t\x00\x00\x9e\xbeMD\xadWED\x18\x00\t\x00\x00\x93\xa1MD\x1ceED\x18\x00\t\x00\x00\x88\x84MD\x8crED\x18\x00\t\x00\x00}gMD\xfc\x7fED\x18\x00\t\x00\x00rJMDk\x8dED\x18\x00\t\x00\x00g-MD\xdb\x9aED\x18\x00\t\x00\x00\\\x10MDJ\xa8ED\x18\x00\t\x00\x00Q\xf3LD\xba\xb5ED\x18\x00\t\x00\x00F\xd6LD)\xc3ED\x18\x00\t\x00\x00;\xb9LD\x99\xd0ED\x18\x00\t\x00\x000\x9cLD\x08\xdeED\x18\x00\t\x00\x00%\x7fLDx\xebED\x18\x00\t\x00\x00\x1abLD\xe7\xf8ED\x18\x00\t\x00\x00\x0fELDW\x06FD\x18\x00\t\x00\x00\x04(LD\xc6\x13FD\x18\x00\t\x00\x00\xf9\nLD6!FD\x18\x00\t\x00\x00\xee\xedKD\xa5.FD\x18\x00\t\x00\x00\xe3\xd0KD\x15<FD\x18\x00\t\x00\x00\xd8\xb3KD\x84IFD\x18\x00\t\x00\x00\xcd\x96KD\xf4VFD\x18\x00\t\x00\x00\xc2yKDcdFD\x18\x00\t\x00\x00\xb7\\KD\xd3qFD\x18\x00\t\x00\x00\xac?KDB\x7fFD\x18\x00\t\x00\x00\xa1"KD\xb2\x8cFD\x18\x00\t\x00\x00\x96\x05KD!\x9aFD\x18\x00\t\x00\x00\x8b\xe8JD\x91\xa7FD\x18\x00\t\x00\x00\x80\xcbJD\x00\xb5FD\x18\x00\t\x00\x00u\xaeJDp\xc2FD\x18\x00\t\x00\x00j\x91JD\xdf\xcfFD\x18\x00\t\x00\x00_tJDO\xddFD\x18\x00\t\x00\x00TWJD\xbe\xeaFD\x18\x00\t\x00\x00I:JD.\xf8FD\x18\x00\t\x00\x00>\x1dJD\x9d\x05GD\x18\x00\t\x00\x003\x00JD\r\x13GD\x18\x00\t\x00\x00(\xe3ID| GD\x18\x00\t\x00\x00\x1d\xc6ID\xec-GD\x18\x00\t\x00\x00\x12\xa9ID\\;GD\x18\x00\t\x00\x00\x07\x8cID\xcbHGD\x18\x00\t\x00\x00\xfcnID;VGD\r\x00\x81\xe5@D\x83\x00SC3#BD\xff\x01t\x00\xd4\x07\x00\x00\x00\x01*\xd4QD|2SC\xfdsCD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00}5\xfc?\x00\x04d\x00\x00\x00\x00\x05d\x00\x00\x00\x00\x06d\x00\x00\x00\x00\x07d\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\n\xe901\x01\x00\x0b\n\x00\x0c2\x00\r\x0c\x00\x00\x00\xe8\x89\xbe\xe5\x85\x8b\xe6\x96\xaf\xe7\x90\x83\x00\x0e\x00\x00\x0f\x00\x00\x10\xe901\x01\x00\x11\x01\x00\x00\x00\xfb\x01\x05\x00\xd4\x07\x00\x00\x05\xff\x01S\x00\xd1\x07\x00\x00\x00\x01\x8e\x01DDM\xf3RCq\x91CD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\xa0\xc40\xc0\x00\x04\x00\x00\x00\x00\x00\x05i\x9a\x98\x00\x00\x06\x0f\x00\x072\x00\x08\x0f\x00\x00\x00\xe6\x96\xb0\xe6\x89\x8b\xe6\x8e\xa5\xe5\xbe\x85\xe5\x91\x98\x00\ti\x9a\x98\x00\x00\n\x01\x00\x00\x00\xfb\x01\x06\x00\xd1\x07\x00\x00\x06\x00\x1d\x00\r\x00\x00\x1f\xb7QDm\x81CD\xaf\x99\x91\xbf\x1d\x00\r\x00\x00\x14\x9aQD\xdd\x8eCD\xaf\x99\x91\xbf\x18\x00\t\x00\x00\t}QDM\x9cCD\x18\x00\t\x00\x00\xfe_QD\xbc\xa9CD\x18\x00\t\x00\x00\xf3BQD,\xb7CD\x18\x00\t\x00\x00\xe8%QD\x9b\xc4CD\x18\x00\t\x00\x00\xdd\x08QD\x0b\xd2CD\x18\x00\t\x00\x00\xd2\xebPDz\xdfCD\x18\x00\t\x00\x00\xc7\xcePD\xea\xecCD\x18\x00\t\x00\x00\xbc\xb1PDZ\xfaCD\x18\x00\t\x00\x00\xb1\x94PD\xc9\x07DD\x18\x00\t\x00\x00\xa6wPD9\x15DD\x18\x00\t\x00\x00\x9bZPD\xa8"DD\x18\x00\t\x00\x00\x90=PD\x180DD\x18\x00\t\x00\x00\x85 PD\x87=DD\x18\x00\t\x00\x00z\x03PD\xf7JDD\x18\x00\t\x00\x00o\xe6ODfXDD\x18\x00\t\x00\x00d\xc9OD\xd6eDD\x18\x00\t\x00\x00Y\xacODEsDD\x18\x00\t\x00\x00N\x8fOD\xb5\x80DD\x18\x00\t\x00\x00CrOD$\x8eDD\x18\x00\t\x00\x008UOD\x94\x9bDD\x18\x00\t\x00\x00-8OD\x03\xa9DD\x18\x00\t\x00\x00"\x1bODs\xb6DD\x18\x00\t\x00\x00\x17\xfeND\xe2\xc3DD\x18\x00\t\x00\x00\x0c\xe1NDR\xd1DD\x18\x00\t\x00\x00\x01\xc4ND\xc1\xdeDD\x18\x00\t\x00\x00\xf6\xa6ND1\xecDD\x18\x00\t\x00\x00\xeb\x89ND\xa0\xf9DD\x18\x00\t\x00\x00\xe0lND\x10\x07ED\x18\x00\t\x00\x00\xd5OND\x7f\x14ED\x18\x00\t\x00\x00\xca2ND\xef!ED\x18\x00\t\x00\x00\xbf\x15ND^/ED\x18\x00\t\x00\x00\xb4\xf8MD\xce<ED\x18\x00\t\x00\x00\xa9\xdbMD=JED\x18\x00\t\x00\x00\x9e\xbeMD\xadWED\x18\x00\t\x00\x00\x93\xa1MD\x1ceED\x18\x00\t\x00\x00\x88\x84MD\x8crED\x18\x00\t\x00\x00}gMD\xfc\x7fED\x18\x00\t\x00\x00rJMDk\x8dED\x18\x00\t\x00\x00g-MD\xdb\x9aED\x18\x00\t\x00\x00\\\x10MDJ\xa8ED\x18\x00\t\x00\x00Q\xf3LD\xba\xb5ED\x18\x00\t\x00\x00F\xd6LD)\xc3ED\x18\x00\t\x00\x00;\xb9LD\x99\xd0ED\x18\x00\t\x00\x000\x9cLD\x08\xdeED\x18\x00\t\x00\x00%\x7fLDx\xebED\x18\x00\t\x00\x00\x1abLD\xe7\xf8ED\x18\x00\t\x00\x00\x0fELDW\x06FD\x18\x00\t\x00\x00\x04(LD\xc6\x13FD\x18\x00\t\x00\x00\xf9\nLD6!FD\x18\x00\t\x00\x00\xee\xedKD\xa5.FD\x18\x00\t\x00\x00\xe3\xd0KD\x15<FD\x18\x00\t\x00\x00\xd8\xb3KD\x84IFD\x18\x00\t\x00\x00\xcd\x96KD\xf4VFD\x18\x00\t\x00\x00\xc2yKDcdFD\x18\x00\t\x00\x00\xb7\\KD\xd3qFD\x18\x00\t\x00\x00\xac?KDB\x7fFD\x18\x00\t\x00\x00\xa1"KD\xb2\x8cFD\x18\x00\t\x00\x00\x96\x05KD!\x9aFD\x18\x00\t\x00\x00\x8b\xe8JD\x91\xa7FD\x18\x00\t\x00\x00\x80\xcbJD\x00\xb5FD\x18\x00\t\x00\x00u\xaeJDp\xc2FD\x18\x00\t\x00\x00j\x91JD\xdf\xcfFD\x18\x00\t\x00\x00_tJDO\xddFD\x18\x00\t\x00\x00TWJD\xbe\xeaFD\x18\x00\t\x00\x00I:JD.\xf8FD\x18\x00\t\x00\x00>\x1dJD\x9d\x05GD\x18\x00\t\x00\x003\x00JD\r\x13GD\x18\x00\t\x00\x00(\xe3ID| GD\x18\x00\t\x00\x00\x1d\xc6ID\xec-GD\x18\x00\t\x00\x00\x12\xa9ID\\;GD\x18\x00\t\x00\x00\x07\x8cID\xcbHGD\x18\x00\t\x00\x00\xfcnID;VGD\x18\x00\t\x00\x00\xf1QID\xaacGD\x18\x00\t\x00\x00\xe64ID\x1aqGD\x18\x00\t\x00\x00\xdb\x17ID\x89~GD\x18\x00\t\x00\x00\xd0\xfaHD\xf9\x8bGD\x18\x00\t\x00\x00\xc5\xddHDh\x99GD\x18\x00\t\x00\x00\xba\xc0HD\xd8\xa6GD\x18\x00\t\x00\x00\xaf\xa3HDG\xb4GD\x18\x00\t\x00\x00\xa4\x86HD\xb7\xc1GD\x18\x00\t\x00\x00\x99iHD&\xcfGD\x18\x00\t\x00\x00\x8eLHD\x96\xdcGD\x18\x00\t\x00\x00\x83/HD\x05\xeaGD\x18\x00\t\x00\x00x\x12HDu\xf7GD\x18\x00\t\x00\x00\x00\x00HD\x00\x00HD\x1d\x00\r\x00\x00Z\xe9GD\x9b\x16HD\xfcNI\xbf\x1d\x00\r\x00\x00\xb4\xd2GD6-HD\xfcNI\xbf\x18\x00\t\x00\x00\x0e\xbcGD\xd1CHD\x18\x00\t\x00\x00h\xa5GDlZHD\x18\x00\t\x00\x00\xc2\x8eGD\x07qHD\x18\x00\t\x00\x00\x1cxGD\xa2\x87HD\x18\x00\t\x00\x00uaGD=\x9eHD\x18\x00\t\x00\x00\x94YGD\x1a\xa6HD\x18\x00\t\x00\x00\x94YGD\x1a\xa6HD\r\x00\x81\xe5@D\x83\x00SC3#BD\xff\x01t\x00\xd4\x07\x00\x00\x00\x01*\xd4QD|2SC\xfdsCD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00}5\xfc?\x00\x04d\x00\x00\x00\x00\x05d\x00\x00\x00\x00\x06d\x00\x00\x00\x00\x07d\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\n\xe901\x01\x00\x0b\n\x00\x0c2\x00\r\x0c\x00\x00\x00\xe8\x89\xbe\xe5\x85\x8b\xe6\x96\xaf\xe7\x90\x83\x00\x0e\x00\x00\x0f\x00\x00\x10\xe901\x01\x00\x11\x01\x00\x00\x00\xfb\x01\x05\x00\xd4\x07\x00\x00\x05\xff\x01S\x00\xd1\x07\x00\x00\x00\x01\x8e\x01DDM\xf3RCq\x91CD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\xa0\xc40\xc0\x00\x04\x00\x00\x00\x00\x00\x05i\x9a\x98\x00\x00\x06\x0f\x00\x072\x00\x08\x0f\x00\x00\x00\xe6\x96\xb0\xe6\x89\x8b\xe6\x8e\xa5\xe5\xbe\x85\xe5\x91\x98\x00\ti\x9a\x98\x00\x00\n\x01\x00\x00\x00\xfb\x01\x06\x00\xd1\x07\x00\x00\x06\x00\x1d\x00\r\x00\x00\x1f\xb7QDm\x81CD\xaf\x99\x91\xbf\x1d\x00\r\x00\x00\x14\x9aQD\xdd\x8eCD\xaf\x99\x91\xbf\x18\x00\t\x00\x00\t}QDM\x9cCD\x18\x00\t\x00\x00\xfe_QD\xbc\xa9CD\x18\x00\t\x00\x00\xf3BQD,\xb7CD\x18\x00\t\x00\x00\xe8%QD\x9b\xc4CD\x18\x00\t\x00\x00\xdd\x08QD\x0b\xd2CD\x18\x00\t\x00\x00\xd2\xebPDz\xdfCD\x18\x00\t\x00\x00\xc7\xcePD\xea\xecCD\x18\x00\t\x00\x00\xbc\xb1PDZ\xfaCD\x18\x00\t\x00\x00\xb1\x94PD\xc9\x07DD\x18\x00\t\x00\x00\xa6wPD9\x15DD\x18\x00\t\x00\x00\x9bZPD\xa8"DD\x18\x00\t\x00\x00\x90=PD\x180DD\x18\x00\t\x00\x00\x85 PD\x87=DD\x18\x00\t\x00\x00z\x03PD\xf7JDD\x18\x00\t\x00\x00o\xe6ODfXDD\x18\x00\t\x00\x00d\xc9OD\xd6eDD\x18\x00\t\x00\x00Y\xacODEsDD\x18\x00\t\x00\x00N\x8fOD\xb5\x80DD\x18\x00\t\x00\x00CrOD$\x8eDD\x18\x00\t\x00\x008UOD\x94\x9bDD\x18\x00\t\x00\x00-8OD\x03\xa9DD\x18\x00\t\x00\x00"\x1bODs\xb6DD\x18\x00\t\x00\x00\x17\xfeND\xe2\xc3DD\x18\x00\t\x00\x00\x0c\xe1NDR\xd1DD\x18\x00\t\x00\x00\x01\xc4ND\xc1\xdeDD\x18\x00\t\x00\x00\xf6\xa6ND1\xecDD\x18\x00\t\x00\x00\xeb\x89ND\xa0\xf9DD\x18\x00\t\x00\x00\xe0lND\x10\x07ED\x18\x00\t\x00\x00\xd5OND\x7f\x14ED\x18\x00\t\x00\x00\xca2ND\xef!ED\x18\x00\t\x00\x00\xbf\x15ND^/ED\x18\x00\t\x00\x00\xb4\xf8MD\xce<ED\x18\x00\t\x00\x00\xa9\xdbMD=JED\x18\x00\t\x00\x00\x9e\xbeMD\xadWED\x18\x00\t\x00\x00\x93\xa1MD\x1ceED\x18\x00\t\x00\x00\x88\x84MD\x8crED\x18\x00\t\x00\x00}gMD\xfc\x7fED\x18\x00\t\x00\x00rJMDk\x8dED\x18\x00\t\x00\x00g-MD\xdb\x9aED\x18\x00\t\x00\x00\\\x10MDJ\xa8ED\x18\x00\t\x00\x00Q\xf3LD\xba\xb5ED\x18\x00\t\x00\x00F\xd6LD)\xc3ED\x18\x00\t\x00\x00;\xb9LD\x99\xd0ED\x18\x00\t\x00\x000\x9cLD\x08\xdeED\x18\x00\t\x00\x00%\x7fLDx\xebED\x18\x00\t\x00\x00\x1abLD\xe7\xf8ED\x18\x00\t\x00\x00\x0fELDW\x06FD\x18\x00\t\x00\x00\x04(LD\xc6\x13FD\x18\x00\t\x00\x00\xf9\nLD6!FD\x18\x00\t\x00\x00\xee\xedKD\xa5.FD\x18\x00\t\x00\x00\xe3\xd0KD\x15<FD\x18\x00\t\x00\x00\xd8\xb3KD\x84IFD\x18\x00\t\x00\x00\xcd\x96KD\xf4VFD\x18\x00\t\x00\x00\xc2yKDcdFD\x18\x00\t\x00\x00\xb7\\KD\xd3qFD\x18\x00\t\x00\x00\xac?KDB\x7fFD\x18\x00\t\x00\x00\xa1"KD\xb2\x8cFD\x18\x00\t\x00\x00\x96\x05KD!\x9aFD\x18\x00\t\x00\x00\x8b\xe8JD\x91\xa7FD\x18\x00\t\x00\x00\x80\xcbJD\x00\xb5FD\x18\x00\t\x00\x00u\xaeJDp\xc2FD\x18\x00\t\x00\x00j\x91JD\xdf\xcfFD\x18\x00\t\x00\x00_tJDO\xddFD\x18\x00\t\x00\x00TWJD\xbe\xeaFD\x18\x00\t\x00\x00I:JD.\xf8FD\x18\x00\t\x00\x00>\x1dJD\x9d\x05GD\x18\x00\t\x00\x003\x00JD\r\x13GD\x18\x00\t'
        msg_13, data_tail = kbeclient.MessageSerializer().deserialize(memoryview(data))
        assert msg_13 is not None, 'Invalid initial data'

        handler = handler.OnUpdateBasePosHandler(self._entity_helper)
        result: handler.HandlerResult = handler.handle(msg_13)
        assert result.success
        assert result.result.position.x == 82720063488.0
        assert result.result.position.y == 285.7286376953125
        assert result.result.position.z == -2.424715948069392e-28
