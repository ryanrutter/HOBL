// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent

import com.microsoft.hobl.agent.inputinject.ScreenStreamer
import com.microsoft.hobl.agent.inputinject.ScreencapSource
import java.io.IOException
import java.net.InetSocketAddress
import java.net.ServerSocket
import kotlin.system.exitProcess

// Aluminium counterpart of utilities/open_source/ScreenServer, used by ScenarioMaker to show the
// DUT screen.  ScenarioMaker starts it through the agent with:
//
//   CLASSPATH=<path>/AluminiumAgent.jar app_process / --nice-name=ScreenServer com.microsoft.hobl.agent.ScreenServer --allow <host_ip>
//
// The process name lets ScenarioMaker find and stop it with pgrep/killall, the same as on macOS.
//
// Options:
//   --port <port>            Stream port (default 8020, the same as ScreenServer).
//   --allow <ip>[,<ip>...]   Hosts allowed to connect.  Loopback is always allowed.
//   --allow-any              Allow any host to connect.
object ScreenServer {
    private const val DEFAULT_PORT = 8020

    @JvmStatic
    fun main(args: Array<String>) {
        var port = DEFAULT_PORT
        val allowed = mutableListOf<String>()
        var allowAny = false

        var i = 0
        while (i < args.size) {
            when (args[i]) {
                "--port" -> port = args.getOrNull(++i)?.toIntOrNull() ?: usage("--port requires a number")
                "--allow" -> allowed += (args.getOrNull(++i) ?: usage("--allow requires an address")).split(",").filter { it.isNotBlank() }
                "--allow-any" -> allowAny = true
                else -> usage("Unknown option: ${args[i]}")
            }
            i++
        }
        if (allowed.isEmpty() && !allowAny) usage("Specify the HOBL host with --allow <ip>, or use --allow-any.")
        val allowList = AllowList(allowed, allowAny)

        val server = ServerSocket()
        server.reuseAddress = true
        server.bind(InetSocketAddress(port))
        println("ScreenServer listening on port $port")

        // One viewer at a time, like the Windows and macOS ScreenServer.
        while (true) {
            val client = server.accept()
            client.use {
                val remote = client.remoteSocketAddress as InetSocketAddress
                if (!allowList.isAllowed(remote.address)) {
                    System.err.println("Rejected connection from ${remote.address.hostAddress}")
                    return@use
                }
                try {
                    ScreenStreamer(ScreencapSource()).serve(client.getOutputStream()) { !client.isClosed }
                } catch (e: IOException) {
                    println("Viewer disconnected: ${e.message}")
                }
            }
        }
    }

    private fun usage(message: String): Nothing {
        System.err.println(" ERROR - $message")
        System.err.println("Usage: app_process / com.microsoft.hobl.agent.ScreenServer --allow <host_ip>[,<ip>...] [--allow-any] [--port <port>]")
        exitProcess(1)
    }
}
