// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent

import android.os.Looper
import android.system.Os
import com.microsoft.hobl.agent.inputinject.Application
import kotlin.system.exitProcess

// Entry point of the HOBL agent for Aluminium (Android desktop) DUTs.  This takes the place of
// SimpleRemote on Windows, macOS, and Linux.  It is pushed to the DUT and started over ADB by
// setup_src/src_dut_aluminium/launch_agent.ps1 with:
//
//   CLASSPATH=<path>/AluminiumAgent.jar setsid app_process / --nice-name=hobl_agent com.microsoft.hobl.agent.Server --allow <host_ip>
//
// Options:
//   --port <port>            RPC port (default 8000, the same as SimpleRemote).
//   --allow <ip>[,<ip>...]   Hosts allowed to connect.  Loopback is always allowed.
//   --allow-any              Allow any host to connect.  Only use on isolated lab networks.
//   --log <path>             Log file.
//   --debug                  Verbose logging.
object Server {
    private const val DEFAULT_PORT = 8000

    @JvmStatic
    fun main(args: Array<String>) {
        var port = DEFAULT_PORT
        val allowed = mutableListOf<String>()
        var allowAny = false
        var logPath: String? = null

        var i = 0
        while (i < args.size) {
            when (args[i]) {
                "--port" -> port = args.getOrNull(++i)?.toIntOrNull() ?: usage("--port requires a number")
                "--allow" -> allowed += (args.getOrNull(++i) ?: usage("--allow requires an address")).split(",").filter { it.isNotBlank() }
                "--allow-any" -> allowAny = true
                "--log" -> logPath = args.getOrNull(++i) ?: usage("--log requires a path")
                "--debug" -> Logger.debugEnabled = true
                else -> usage("Unknown option: ${args[i]}")
            }
            i++
        }
        if (allowed.isEmpty() && !allowAny) usage("Specify the HOBL host with --allow <ip>, or use --allow-any on isolated lab networks.")

        logPath?.let { Logger.open(it) }
        Logger.info("HOBL Aluminium agent ${BuildConfig.VERSION_NAME} starting.")
        println("WARNING: This agent allows the allowed hosts to run programs and access files on this device with no authentication.")
        println("         Only use it on dedicated test devices.")

        // Detach from the ADB session, so the agent keeps running after USB is unplugged or ADB disconnects.
        try {
            Os.setsid()
        } catch (e: Exception) {
            Logger.debug("setsid() not applied: ${e.message}")
        }

        // Some framework services used for input injection expect a Looper on the main thread.
        try {
            @Suppress("DEPRECATION")
            Looper.prepareMainLooper()
        } catch (e: Exception) {
            Logger.debug("prepareMainLooper() not applied: ${e.message}")
        }

        val location = System.getProperty("java.class.path").orEmpty()
        val functions = Functions(BuildConfig.VERSION_NAME, location) { identifier, className, path ->
            if (className != Application.CLASS_NAME) {
                throw IllegalArgumentException("Plugin class $className is not supported on Aluminium.")
            }
            Logger.info("Loading plugin $identifier ($className); path '$path' is provided by the agent.")
            Application.create()
        }

        try {
            SimpleRpcServer(functions, AllowList(allowed, allowAny)).start(port)
        } catch (e: Exception) {
            Logger.error("Server failed.", e)
            System.err.println(" ERROR - Server failed: $e")
            exitProcess(1)
        }
    }

    private fun usage(message: String): Nothing {
        System.err.println(" ERROR - $message")
        System.err.println("Usage: app_process / com.microsoft.hobl.agent.Server --allow <host_ip>[,<ip>...] [--allow-any] [--port <port>] [--log <path>] [--debug]")
        exitProcess(1)
    }
}
