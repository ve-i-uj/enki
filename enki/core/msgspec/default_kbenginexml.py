class root:
    gameUpdateHertz: int = 10
    bitsPerSecondToClient: int = 20000
    packetAlwaysContainLength: int = 0

    class trace_packet:
        debug_type: int = 0
        use_logfile: bool = False

        class disables:
            item: list[str] = [
                "Encrypted::packets",
                "Baseappmgr::updateBaseapp",
                "Baseappmgr::onBaseappInitProgress",
                "Cellappmgr::updateCellapp",
                "Cellappmgr::onCellappInitProgress",
                "Loginapp::onBaseappInitProgress",
                "Cellapp::onUpdateDataFromClient",
                "Baseapp::onUpdateDataFromClient",
                "Baseapp::forwardMessageToClientFromCellapp",
                "Client::onUpdateVolatileData",
                "Client::onUpdateData",
                "Client::onUpdateBasePos",
                "Client::onUpdateData_xz",
                "Client::onUpdateData_xyz",
                "Client::onUpdateData_y",
                "Client::onUpdateData_r",
                "Client::onUpdateData_p",
                "Client::onUpdateData_ypr",
                "Client::onUpdateData_yp",
                "Client::onUpdateData_yr",
                "Client::onUpdateData_pr",
                "Client::onUpdateData_xz_y",
                "Client::onUpdateData_xz_p",
                "Client::onUpdateData_xz_r",
                "Client::onUpdateData_xz_yr",
                "Client::onUpdateData_xz_yp",
                "Client::onUpdateData_xz_pr",
                "Client::onUpdateData_xz_ypr",
                "Client::onUpdateData_xyz_y",
                "Client::onUpdateData_xyz_p",
                "Client::onUpdateData_xyz_r",
                "Client::onUpdateData_xyz_yr",
                "Client::onUpdateData_xyz_yp",
                "Client::onUpdateData_xyz_pr",
                "Client::onUpdateData_xyz_ypr"
            ]
    debugEntity: int = 0

    class publish:
        state: int = 0
        script_version: str = "0.1.0"

    class channelCommon:
        class timeout:
            internal: float = 60.0
            external: float = 60.0

        class readBufferSize:
            internal: int = 16777216
            external: int = 0

        class writeBufferSize:
            internal: int = 16777216
            external: int = 0

        class windowOverflow:
            class send:
                class tickSentBytes:
                    internal: int = 0
                    external: int = 0

                class messages:
                    critical: int = 1024
                    internal: int = 65535
                    external: int = 512

                class bytes:
                    internal: int = 0
                    external: int = 1048576

            class receive:
                class messages:
                    critical: int = 24
                    internal: int = 65535
                    external: int = 32

                class bytes:
                    internal: int = 0
                    external: int = 2048

        encrypt_type: int = 1

        class reliableUDP:
            class readPacketsQueueSize:
                internal: int = 1024
                external: int = 128

            class writePacketsQueueSize:
                internal: int = 1024
                external: int = 128

            tickInterval: int = 10
            minRTO: int = 10
            missAcksResend: int = 2
            mtu: int = 0
            congestionControl: bool = False
            nodelay: bool = True

        sslCertificate: str = "key/server_cert.pem"
        sslPrivateKey: str = "key/server_key.pem"

    shutdown_time: float = 30.0
    shutdown_waittick: float = 1.0
    callback_timeout: float = 300.0

    class thread_pool:
        timeout: float = 300.0
        init_create: int = 1
        pre_create: int = 2
        max_create: int = 8

    email_service_config: str = "server/email_service_defaults.xml"

    class interfaces:
        entryScriptFile: str = "kbemain"
        host: str = "localhost"
        port_min: int = 30099
        port_max: int = 30199
        orders_timeout: int = 3600
        SOMAXCONN: int = 511

        class telnet_service:
            port: int = 33000
            password: str = "pwd123456"
            default_layer: str = "python"

        # for old version kbengine
        port = port_min

    class dbmgr:
        entryScriptFile: str = "kbemain"
        debug: bool = False
        shareDB: bool = False
        allowEmptyDigest: bool = False
        internalInterface: str = ''

        class InterfacesServiceAddr:
            enable: bool = True
            addDefaultAddress: bool = True

            class item:
                host: str = 'localhost1'
                port: int = 30098

        class databaseInterfaces:
            class default:
                pure: bool = False
                type: str = "mysql"
                host: str = "localhost"
                port: int = 0

                class auth:
                    username: str = "kbe"
                    password: str = "pwd123456"
                    encrypt: bool = True

                databaseName: str = "kbe"
                numConnections: int = 5

                class unicodeString:
                    characterSet: str = "utf8mb4"
                    collation: str = "utf8mb4_bin"

        class account_system:
            accountEntityScriptType: str = "Account"
            accountDefaultFlags: int = 0
            accountDefaultDeadline: int = 0

            class account_resetPassword:
                enable: bool = False

            class account_registration:
                enable: bool = False
                loginAutoCreate: bool = False

        class telnet_service:
            port: int = 32000
            password: str = "pwd123456"
            default_layer: str = "python"

        class ids:
            increasing_range: int = 2000

        SOMAXCONN: int = 511

    class cellapp:
        entryScriptFile: str = "kbemain"

        class defaultViewRadius:
            radius: float = 80.0
            hysteresisArea: float = 5.0

        aliasEntityID: bool = True
        entitydefAliasID: bool = True
        internalInterface: str = ''

        class ids:
            criticallyLowSize: int = 1000

        class profiles:
            cprofile: bool = False
            pyprofile: bool = False
            eventprofile: bool = False
            networkprofile: bool = False

        loadSmoothingBias: float = 0.01
        ghostDistance: float = 500.0
        ghostingMaxPerCheck: int = 64
        ghostUpdateHertz: int = 30

        class coordinate_system:
            enable: bool = True
            rangemgr_y: bool = False
            entity_posdir_additional_updates: int = 2

            class entity_posdir_updates:
                type: int = 2
                smartThreshold: int = 10

        class telnet_service:
            port: int = 50000
            password: str = "pwd123456"
            default_layer: str = "python"

        class shutdown:
            perSecsDestroyEntitySize: int = 100

        class witness:
            timeout: int = 15

        SOMAXCONN: int = 511

    class baseapp:
        entryScriptFile: str = "kbemain"
        internalInterface: str = ''
        externalInterface: str = ''
        externalAddress: str = ''
        externalTcpPorts_min: int = 20015
        externalTcpPorts_max: int = 20019
        externalUdpPorts_min: int = 20005
        externalUdpPorts_max: int = 20009
        archivePeriod: int = 300
        backupPeriod: int = 300
        backUpUndefinedProperties: int = 0
        loadSmoothingBias: float = 0.01

        class downloadStreaming:
            bitsPerSecondTotal: int = 1000000
            bitsPerSecondPerClient: int = 100000

        class ids:
            criticallyLowSize: int = 1000

        entityRestoreSize: int = 32

        class profiles:
            cprofile: bool = False
            pyprofile: bool = False
            eventprofile: bool = False
            networkprofile: bool = False

        SOMAXCONN: int = 511

        class telnet_service:
            port: int = 40000
            password: str = "pwd123456"
            default_layer: str = "python"

        class shutdown:
            perSecsDestroyEntitySize: int = 100

        class respool:
            buffer_size: int = 1024
            timeout: int = 600
            checktick: int = 60

    class cellappmgr:
        SOMAXCONN: int = 511
        internalInterface: str = ''

    class baseappmgr:
        SOMAXCONN: int = 511
        internalInterface: str = ''

    class loginapp:
        entryScriptFile: str = "kbemain"
        internalInterface: str = ''
        externalInterface: str = ''
        externalAddress: str = ''
        externalTcpPorts_min: int = 20013
        externalTcpPorts_max: int = 0
        externalUdpPorts_min: int = -1
        externalUdpPorts_max: int = -1
        encrypt_login: int = 2
        SOMAXCONN: int = 511
        account_type: int = 3
        http_cbhost: str = "localhost"
        http_cbport: int = 21103

        class telnet_service:
            port: int = 31000
            password: str = "pwd123456"
            default_layer: str = "python"

    class machine:
        externalTcpPorts_min: int = 20099
        externalTcpPorts_max: int = 0
        externalUdpPorts_min: int = 0
        externalUdpPorts_max: int = 0

        class addresses:
            item: list[str] = [
            ]

    class bots:
        entryScriptFile: str = "kbemain"
        internalInterface: str = ''
        forceInternalLogin: bool = False
        host: str = "localhost"
        port_min: int = 20013
        port_max: int = 0
        isOnInitCallPropertysSetMethods: bool = True

        class defaultAddBots:
            totalCount: int = 10
            tickTime: float = 0.1
            tickCount: int = 5

        class account_infos:
            account_name_prefix: str = "bot_"
            account_name_suffix_inc: int = 0
            account_password: str = "pwd123456"

        class telnet_service:
            port: int = 51000
            password: str = "pwd123456"
            default_layer: str = "python"

    class logger:
        entryScriptFile: str = "kbemain"
        internalInterface: str = ''
        tick_max_buffered_logs: int = 131070
        tick_sync_logs: int = 0

        class telnet_service:
            port: int = 34000
            password: str = "pwd123456"
            default_layer: str = "python"

        SOMAXCONN: int = 511
