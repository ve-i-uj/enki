python tools/msgreader --log-level=INFO \
    pcap \
        --show-data \
        --parse-msg \
        --component-name-by-ip-file tools/msgreader/data/component-name-by-ip.file \
        --pcap-files-directory /tmp/kbedump \
        --ignored-msgs \
            Machine::onLookApp \
            Machine::lookApp \
            Machine::onBroadcastInterface \
            Machine::onFindInterfaceAddr  \
            \
            Logger::writeLog \
            Logger::onAppActiveTick \
            Logger::onRegisterNewApp \
            Logger::lookApp \
            Logger::onLookApp \
            \
            Interfaces::onAccountLogin \
            Interfaces::onRegisterNewApp \
            Interfaces::onLookApp \
            Interfaces::lookApp \
            \
            Dbmgr::onAppActiveTick \
            Dbmgr::onLoginAccountCBBFromInterfaces \
            Dbmgr::onEntityOffline \
            Dbmgr::writeEntity \
            Dbmgr::queryAccount \
            Dbmgr::onAccountLogin \
            Dbmgr::entityAutoLoad \
            Dbmgr::onRegisterNewApp \
            Dbmgr::syncEntityStreamTemplate \
            Dbmgr::lookApp \
            Dbmgr::onLookApp \
            \
            Cellappmgr::updateCellapp \
            Cellappmgr::onAppActiveTick \
            Cellappmgr::onRegisterNewApp \
            Cellappmgr::onCellappInitProgress \
            Cellappmgr::lookApp \
            Cellappmgr::onLookApp \
            \
            Baseappmgr::updateBaseapp \
            Baseappmgr::onAppActiveTick \
            Baseappmgr::onPendingAccountGetBaseappAddr \
            Baseappmgr::registerPendingAccountToBaseapp \
            Baseappmgr::onBaseappInitProgress \
            Baseappmgr::onRegisterNewApp \
            Baseappmgr::lookApp \
            Baseappmgr::onLookApp \
            \
            Cellapp::onAppActiveTick\
            Cellapp::onRegisterNewApp \
            Cellapp::onDbmgrInitCompleted \
            Cellapp::lookApp \
            Cellapp::reqBackupEntityCellData \
            \
            Baseapp::onQueryAccountCBFromDbmgr \
            Baseapp::onAppActiveTick \
            Baseapp::registerPendingLogin \
            Baseapp::loginBaseapp \
            Baseapp::onWriteToDBCallback \
            Baseapp::hello \
            Baseapp::onClientActiveTick \
            Baseapp::onEntityAutoLoadCBFromDbmgr \
            Baseapp::onGetEntityAppFromDbmgr \
            Baseapp::onDbmgrInitCompleted \
            Baseapp::lookApp \
            Baseapp::onLookApp \
            Baseapp::onBackupEntityCellData \
            \
            Loginapp::onAppActiveTick \
            Loginapp::onLoginAccountQueryBaseappAddrFromBaseappmgr \
            Loginapp::onLoginAccountQueryResultFromDbmgr \
            Loginapp::hello \
            Loginapp::onBaseappInitProgress \
            Loginapp::login \
            Loginapp::onDbmgrInitCompleted \
            Loginapp::lookApp \
            Loginapp::onLookApp

