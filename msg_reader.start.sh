python tools/msgreader --log-level=DEBUG \
    pcap \
        --parse-msg \
        --show-data \
        --component-name-by-ip-file tools/msgreader/data/component-name-by-ip.file \
        --pcap-files-directory "/home/leto/2PeopleCompany/WORKLOG/20250909 [enki] Переписать msgreader/20260125/kbedump" \
        --ignored-msgs \
            Machine::onLookApp \
            Machine::lookApp \
            Machine::onBroadcastInterface \
            Machine::onFindInterfaceAddr  \
            \
            Logger::writeLog \
            Logger::onAppActiveTick \
            Logger::onRegisterNewApp \
            \
            Interfaces::onAccountLogin \
            Interfaces::onRegisterNewApp \
            \
            DBMgr::onAppActiveTick \
            DBMgr::onLoginAccountCBBFromInterfaces \
            DBMgr::onEntityOffline \
            DBMgr::writeEntity \
            DBMgr::queryAccount \
            DBMgr::onAccountLogin \
            DBMgr::entityAutoLoad \
            DBMgr::onRegisterNewApp \
            DBMgr::syncEntityStreamTemplate \
            \
            CellappMgr::updateCellapp \
            CellappMgr::onAppActiveTick \
            CellappMgr::onRegisterNewApp \
            CellappMgr::onCellappInitProgress \
            \
            BaseappMgr::updateBaseapp \
            BaseappMgr::onAppActiveTick \
            BaseappMgr::onPendingAccountGetBaseappAddr \
            BaseappMgr::registerPendingAccountToBaseapp \
            BaseappMgr::onBaseappInitProgress \
            BaseappMgr::onRegisterNewApp \
            \
            Cellapp::onAppActiveTick\
            Cellapp::onRegisterNewApp \
            Cellapp::onDbmgrInitCompleted \
            \
            Baseapp::onQueryAccountCBFromDbmgr \
            Baseapp::onAppActiveTick \
            Baseapp::registerPendingLogin \
            Baseapp::loginBaseapp \
            Baseapp::onWriteToDBCallback \
            Baseapp::hello \
            Baseapp::onClientActiveTick \
            Baseapp::onEntityAutoLoadCBFromDBMgr \
            Baseapp::onGetEntityAppFromDbmgr \
            Baseapp::onDbmgrInitCompleted \
            \
            Loginapp::onAppActiveTick \
            Loginapp::onLoginAccountQueryBaseappAddrFromBaseappmgr \
            Loginapp::onLoginAccountQueryResultFromDbmgr \
            Loginapp::hello \
            Loginapp::onBaseappInitProgress \
            Loginapp::login \
            Loginapp::onDbmgrInitCompleted \
            \
            Client::onCreatedProxies \
            Client::onAppActiveTickCB \
            Client::onUpdatePropertys \
            Client::onHelloCB \
            Client::onLoginSuccessfully \
    > /tmp/msgreader.info.log

