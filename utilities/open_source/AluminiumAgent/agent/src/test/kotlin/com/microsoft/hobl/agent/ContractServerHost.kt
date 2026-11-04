// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent

import com.microsoft.hobl.agent.inputinject.Application
import com.microsoft.hobl.agent.inputinject.GradientScreen
import com.microsoft.hobl.agent.inputinject.Interop
import com.microsoft.hobl.agent.inputinject.RecordingInjector
import com.microsoft.hobl.agent.inputinject.ScreenStreamer
import org.junit.Assume.assumeTrue
import org.junit.Test
import java.io.File

// Hosts the agent's RPC server in the unit test JVM so HOBL's real Python client (core/call_rpc.py)
// can be tested against it from tests/aluminium/test_agent_contract.py.  Skipped unless that test
// sets HOBL_AGENT_CONTRACT_DIR.  InputInject uses a recording injector and a synthetic 64x48 screen;
// the "Test.Recorder" plugin returns the injected events.  The synthetic screen is also streamed with
// the ScreenServer protocol, on the port written to the "screen_port" file.
class ContractServerHost {
    @Test
    fun hostContractServer() {
        val dir = System.getenv("HOBL_AGENT_CONTRACT_DIR")
        assumeTrue("HOBL_AGENT_CONTRACT_DIR is not set", dir != null)
        val contractDir = File(dir!!)
        Logger.open(File(contractDir, "agent.log").path)

        val injector = RecordingInjector()
        val functions = Functions(BuildConfig.VERSION_NAME, "contract") { _, className, _ ->
            when (className) {
                Application.CLASS_NAME -> Application(Interop(injector, GradientScreen()))
                "Test.Recorder" -> object : Plugin {
                    override fun call(method: String, args: RpcArgs): Any? = when (method) {
                        "Events" -> injector.events.toList()
                        "Clear" -> { injector.events.clear(); null }
                        else -> throw IllegalArgumentException("Method $method not found")
                    }
                }
                else -> throw IllegalArgumentException("Plugin class $className is not supported on Aluminium.")
            }
        }
        val server = SimpleRpcServer(functions, AllowList(emptyList()))

        // Also stream the synthetic screen with the ScreenServer protocol on an ephemeral port.
        val screenServer = java.net.ServerSocket(0, 1, java.net.InetAddress.getLoopbackAddress())
        Thread {
            while (!screenServer.isClosed) {
                try {
                    screenServer.accept().use { client ->
                        ScreenStreamer(GradientScreen()).serve(client.getOutputStream()) { !client.isClosed }
                    }
                } catch (_: java.io.IOException) {
                }
            }
        }.apply { isDaemon = true }.start()

        // Stop when the Python side creates the "stop" file, or after 30 minutes.
        Thread {
            val stop = File(contractDir, "stop")
            val deadline = System.currentTimeMillis() + 30 * 60 * 1000
            while (!stop.exists() && System.currentTimeMillis() < deadline) Thread.sleep(200)
            screenServer.close()
            server.stop()
        }.apply { isDaemon = true }.start()

        server.start(0) { port ->
            File(contractDir, "screen_port").writeText(screenServer.localPort.toString())
            val portFile = File(contractDir, "port")
            File(contractDir, "port.tmp").apply { writeText(port.toString()) }.renameTo(portFile)
        }
    }
}
