python tools/msgreader --log-level=INFO \
    pcap \
        --parse-msg \
        --show-data \
        --component-name-by-ip-file tools/msgreader/data/component-name-by-ip.file \
        --pcap-files-directory /tmp/kbedump \
        --ignored-msgs \
            Machine::onLookApp \
            Machine::lookApp \
            Machine::onFindInterfaceAddr \
            Machine::onBroadcastInterface \
            \
            Logger::writeLog \
            Logger::onAppActiveTick \
            Logger::onRegisterNewApp \
            Logger::lookApp \
            Logger::onLookApp \
            \
            Interfaces::onRegisterNewApp \
            Interfaces::onLookApp \
            Interfaces::lookApp \
            \
            Dbmgr::onAppActiveTick \
            Dbmgr::onRegisterNewApp \
            Dbmgr::lookApp \
            Dbmgr::onLookApp \
            \
            Cellappmgr::onAppActiveTick \
            Cellappmgr::onRegisterNewApp \
            Cellappmgr::updateCellapp \
            Cellappmgr::lookApp \
            Cellappmgr::onLookApp \
            \
            Baseappmgr::onAppActiveTick \
            Baseappmgr::onRegisterNewApp \
            Baseappmgr::updateBaseapp \
            Baseappmgr::lookApp \
            Baseappmgr::onLookApp \
            \
            Cellapp::onAppActiveTick\
            Cellapp::onRegisterNewApp \
            Cellapp::lookApp \
            \
            Baseapp::onAppActiveTick \
            Baseapp::lookApp \
            Baseapp::onLookApp \
            \
            Loginapp::onAppActiveTick \
            Loginapp::lookApp \
            Loginapp::onLookApp

