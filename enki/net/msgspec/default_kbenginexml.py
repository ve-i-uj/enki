class root:
    @property
    def gameUpdateHertz(self) -> int: return None

    @property
    def bitsPerSecondToClient(self) -> int: return None

    @property
    def packetAlwaysContainLength(self) -> int: return None

    class trace_packet:
        @property
        def debug_type(self) -> int: return None

        @property
        def use_logfile(self) -> bool: return None

        class disables:
            @property
            def item(self) -> list[str]: return None

    @property
    def debugEntity(self) -> int: return None


    class publish:
        @property
        def state(self) -> int: return None

        @property
        def script_version(self) -> str: return None


    class channelCommon:
        class timeout:
            @property
            def internal(self) -> float: return None

            @property
            def external(self) -> float: return None


        class readBufferSize:
            @property
            def internal(self) -> int: return None

            @property
            def external(self) -> int: return None


        class writeBufferSize:
            @property
            def internal(self) -> int: return None

            @property
            def external(self) -> int: return None


        class windowOverflow:
            class send:
                class tickSentBytes:
                    @property
                    def internal(self) -> int: return None

                    @property
                    def external(self) -> int: return None


                class messages:
                    @property
                    def critical(self) -> int: return None

                    @property
                    def internal(self) -> int: return None

                    @property
                    def external(self) -> int: return None


                class bytes:
                    @property
                    def internal(self) -> int: return None

                    @property
                    def external(self) -> int: return None


            class receive:
                class messages:
                    @property
                    def critical(self) -> int: return None

                    @property
                    def internal(self) -> int: return None

                    @property
                    def external(self) -> int: return None


                class bytes:
                    @property
                    def internal(self) -> int: return None

                    @property
                    def external(self) -> int: return None


        @property
        def encrypt_type(self) -> int: return None


        class reliableUDP:
            class readPacketsQueueSize:
                @property
                def internal(self) -> int: return None

                @property
                def external(self) -> int: return None


            class writePacketsQueueSize:
                @property
                def internal(self) -> int: return None

                @property
                def external(self) -> int: return None


            @property
            def tickInterval(self) -> int: return None

            @property
            def minRTO(self) -> int: return None

            @property
            def missAcksResend(self) -> int: return None

            @property
            def mtu(self) -> int: return None

            @property
            def congestionControl(self) -> bool: return None

            @property
            def nodelay(self) -> bool: return None


        @property
        def sslCertificate(self) -> str: return None

        @property
        def sslPrivateKey(self) -> str: return None


    @property
    def shutdown_time(self) -> float: return None

    @property
    def shutdown_waittick(self) -> float: return None

    @property
    def callback_timeout(self) -> float: return None


    class thread_pool:
        @property
        def timeout(self) -> float: return None

        @property
        def init_create(self) -> int: return None

        @property
        def pre_create(self) -> int: return None

        @property
        def max_create(self) -> int: return None


    @property
    def email_service_config(self) -> str: return None


    class interfaces:
        @property
        def entryScriptFile(self) -> str: return None

        @property
        def host(self) -> str: return None

        @property
        def port_min(self) -> int: return None

        @property
        def port_max(self) -> int: return None

        @property
        def orders_timeout(self) -> int: return None

        @property
        def SOMAXCONN(self) -> int: return None


        class telnet_service:
            @property
            def port(self) -> int: return None

            @property
            def password(self) -> str: return None

            @property
            def default_layer(self) -> str: return None


        # for old version kbengine
        port = port_min

    class dbmgr:
        @property
        def entryScriptFile(self) -> str: return None

        @property
        def debug(self) -> bool: return None

        @property
        def shareDB(self) -> bool: return None

        @property
        def allowEmptyDigest(self) -> bool: return None

        @property
        def internalInterface(self) -> str: return None


        class InterfacesServiceAddr:
            @property
            def enable(self) -> bool: return None

            @property
            def addDefaultAddress(self) -> bool: return None


            class item:
                @property
                def host(self) -> str: return None

                @property
                def port(self) -> int: return None


        class databaseInterfaces:
            class default:
                @property
                def pure(self) -> bool: return None

                @property
                def type(self) -> str: return None

                @property
                def host(self) -> str: return None

                @property
                def port(self) -> int: return None


                class auth:
                    @property
                    def username(self) -> str: return None

                    @property
                    def password(self) -> str: return None

                    @property
                    def encrypt(self) -> bool: return None


                @property
                def databaseName(self) -> str: return None

                @property
                def numConnections(self) -> int: return None


                class unicodeString:
                    @property
                    def characterSet(self) -> str: return None

                    @property
                    def collation(self) -> str: return None


        class account_system:
            @property
            def accountEntityScriptType(self) -> str: return None

            @property
            def accountDefaultFlags(self) -> int: return None

            @property
            def accountDefaultDeadline(self) -> int: return None


            class account_resetPassword:
                @property
                def enable(self) -> bool: return None


            class account_registration:
                @property
                def enable(self) -> bool: return None

                @property
                def loginAutoCreate(self) -> bool: return None


        class telnet_service:
            @property
            def port(self) -> int: return None

            @property
            def password(self) -> str: return None

            @property
            def default_layer(self) -> str: return None


        class ids:
            @property
            def increasing_range(self) -> int: return None


        @property
        def SOMAXCONN(self) -> int: return None


    class cellapp:
        @property
        def entryScriptFile(self) -> str: return None


        class defaultViewRadius:
            @property
            def radius(self) -> float: return None

            @property
            def hysteresisArea(self) -> float: return None


        @property
        def aliasEntityID(self) -> bool: return None

        @property
        def entitydefAliasID(self) -> bool: return None

        @property
        def internalInterface(self) -> str: return None


        class ids:
            @property
            def criticallyLowSize(self) -> int: return None


        class profiles:
            @property
            def cprofile(self) -> bool: return None

            @property
            def pyprofile(self) -> bool: return None

            @property
            def eventprofile(self) -> bool: return None

            @property
            def networkprofile(self) -> bool: return None


        @property
        def loadSmoothingBias(self) -> float: return None

        @property
        def ghostDistance(self) -> float: return None

        @property
        def ghostingMaxPerCheck(self) -> int: return None

        @property
        def ghostUpdateHertz(self) -> int: return None


        class coordinate_system:
            @property
            def enable(self) -> bool: return None

            @property
            def rangemgr_y(self) -> bool: return None

            @property
            def entity_posdir_additional_updates(self) -> int: return None


            class entity_posdir_updates:
                @property
                def type(self) -> int: return None

                @property
                def smartThreshold(self) -> int: return None


        class telnet_service:
            @property
            def port(self) -> int: return None

            @property
            def password(self) -> str: return None

            @property
            def default_layer(self) -> str: return None


        class shutdown:
            @property
            def perSecsDestroyEntitySize(self) -> int: return None


        class witness:
            @property
            def timeout(self) -> int: return None


        @property
        def SOMAXCONN(self) -> int: return None


    class baseapp:
        @property
        def entryScriptFile(self) -> str: return None

        @property
        def internalInterface(self) -> str: return None

        @property
        def externalInterface(self) -> str: return None

        @property
        def externalAddress(self) -> str: return None

        @property
        def externalTcpPorts_min(self) -> int: return None

        @property
        def externalTcpPorts_max(self) -> int: return None

        @property
        def externalUdpPorts_min(self) -> int: return None

        @property
        def externalUdpPorts_max(self) -> int: return None

        @property
        def archivePeriod(self) -> int: return None

        @property
        def backupPeriod(self) -> int: return None

        @property
        def backUpUndefinedProperties(self) -> int: return None

        @property
        def loadSmoothingBias(self) -> float: return None


        class downloadStreaming:
            @property
            def bitsPerSecondTotal(self) -> int: return None

            @property
            def bitsPerSecondPerClient(self) -> int: return None


        class ids:
            @property
            def criticallyLowSize(self) -> int: return None


        @property
        def entityRestoreSize(self) -> int: return None


        class profiles:
            @property
            def cprofile(self) -> bool: return None

            @property
            def pyprofile(self) -> bool: return None

            @property
            def eventprofile(self) -> bool: return None

            @property
            def networkprofile(self) -> bool: return None


        @property
        def SOMAXCONN(self) -> int: return None


        class telnet_service:
            @property
            def port(self) -> int: return None

            @property
            def password(self) -> str: return None

            @property
            def default_layer(self) -> str: return None


        class shutdown:
            @property
            def perSecsDestroyEntitySize(self) -> int: return None


        class respool:
            @property
            def buffer_size(self) -> int: return None

            @property
            def timeout(self) -> int: return None

            @property
            def checktick(self) -> int: return None


    class cellappmgr:
        @property
        def SOMAXCONN(self) -> int: return None

        @property
        def internalInterface(self) -> str: return None


    class baseappmgr:
        @property
        def SOMAXCONN(self) -> int: return None

        @property
        def internalInterface(self) -> str: return None


    class loginapp:
        @property
        def entryScriptFile(self) -> str: return None

        @property
        def internalInterface(self) -> str: return None

        @property
        def externalInterface(self) -> str: return None

        @property
        def externalAddress(self) -> str: return None

        @property
        def externalTcpPorts_min(self) -> int: return None

        @property
        def externalTcpPorts_max(self) -> int: return None

        @property
        def externalUdpPorts_min(self) -> int: return None

        @property
        def externalUdpPorts_max(self) -> int: return None

        @property
        def encrypt_login(self) -> int: return None

        @property
        def SOMAXCONN(self) -> int: return None

        @property
        def account_type(self) -> int: return None

        @property
        def http_cbhost(self) -> str: return None

        @property
        def http_cbport(self) -> int: return None


        class telnet_service:
            @property
            def port(self) -> int: return None

            @property
            def password(self) -> str: return None

            @property
            def default_layer(self) -> str: return None


    class machine:
        @property
        def externalTcpPorts_min(self) -> int: return None

        @property
        def externalTcpPorts_max(self) -> int: return None

        @property
        def externalUdpPorts_min(self) -> int: return None

        @property
        def externalUdpPorts_max(self) -> int: return None


        class addresses:
            @property
            def item(self) -> list[str]: return None

            ]

    class bots:
        @property
        def entryScriptFile(self) -> str: return None

        @property
        def internalInterface(self) -> str: return None

        @property
        def forceInternalLogin(self) -> bool: return None

        @property
        def host(self) -> str: return None

        @property
        def port_min(self) -> int: return None

        @property
        def port_max(self) -> int: return None

        @property
        def isOnInitCallPropertysSetMethods(self) -> bool: return None


        class defaultAddBots:
            @property
            def totalCount(self) -> int: return None

            @property
            def tickTime(self) -> float: return None

            @property
            def tickCount(self) -> int: return None


        class account_infos:
            @property
            def account_name_prefix(self) -> str: return None

            @property
            def account_name_suffix_inc(self) -> int: return None

            @property
            def account_password(self) -> str: return None


        class telnet_service:
            @property
            def port(self) -> int: return None

            @property
            def password(self) -> str: return None

            @property
            def default_layer(self) -> str: return None


    class logger:
        @property
        def entryScriptFile(self) -> str: return None

        @property
        def internalInterface(self) -> str: return None

        @property
        def tick_max_buffered_logs(self) -> int: return None

        @property
        def tick_sync_logs(self) -> int: return None


        class telnet_service:
            @property
            def port(self) -> int: return None

            @property
            def password(self) -> str: return None

            @property
            def default_layer(self) -> str: return None


        @property
        def SOMAXCONN(self) -> int: return None

