// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent

import org.json.JSONArray
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.io.IOException
import java.io.InputStream
import java.lang.reflect.InvocationTargetException
import java.net.InetAddress
import java.net.InetSocketAddress
import java.net.ServerSocket
import java.net.Socket
import java.net.SocketTimeoutException
import java.nio.charset.StandardCharsets
import java.util.Base64

// Only hosts in this list may connect.  Loopback is always allowed so the agent can be reached
// through "adb forward".  Unlike SimpleRemote this agent refuses other clients, because Googlebooks
// may be brought up on networks that are not isolated lab networks.
class AllowList(addresses: Collection<String>, private val allowAny: Boolean = false) {
    private val allowed = addresses.map { InetAddress.getByName(it.trim()) }.toSet()

    fun isAllowed(address: InetAddress): Boolean = allowAny || address.isLoopbackAddress || address in allowed

    override fun toString(): String = if (allowAny) "any" else allowed.joinToString(",") { it.hostAddress ?: "" }
}

// Mirrors SimpleJsonRpc.SimpleRpcServer: one newline-terminated JSON-RPC request per connection,
// one newline-terminated response, then the connection is closed.
class SimpleRpcServer(private val functions: Functions, private val allowList: AllowList) {
    private var serverSocket: ServerSocket? = null

    fun start(port: Int, onListening: (Int) -> Unit = {}) {
        val server = ServerSocket()
        server.reuseAddress = true
        server.bind(InetSocketAddress(port))
        serverSocket = server
        Logger.info("RPC Server started on port ${server.localPort}.  Allowed clients: $allowList")
        onListening(server.localPort)

        while (!server.isClosed) {
            val client = try {
                server.accept()
            } catch (e: IOException) {
                if (server.isClosed) break else throw e
            }
            Thread({ handleClient(client) }, "RpcClient").apply { isDaemon = true }.start()
        }
        Logger.info("Server stopped")
    }

    fun stop() {
        serverSocket?.close()
    }

    fun handleClient(client: Socket) {
        client.use {
            val remote = client.remoteSocketAddress as InetSocketAddress
            if (!allowList.isAllowed(remote.address)) {
                // Reply with an explanation instead of dropping the connection, since the host's IP
                // address can change, for example when DHCP leases are renewed.
                val host = remote.address.hostAddress
                Logger.warn("Rejected connection from $host, which is not in the allowed client list.")
                val error = JSONObject().put("jsonrpc", "2.0").put("id", 0)
                    .put("error", "Host $host is not allowed to connect to the agent.  Run launch_agent.ps1 from this host to allow it.")
                client.getOutputStream().write((error.toString() + "\n").toByteArray(StandardCharsets.UTF_8))
                client.getOutputStream().flush()
                return
            }
            Logger.debug("Client connected: ${remote.address.hostAddress}")

            // Drop clients that take more than 10 seconds to send their request.
            client.soTimeout = 10 * 1000
            val request = try {
                readLine(client.getInputStream())
            } catch (e: SocketTimeoutException) {
                Logger.info("Connection timed out.")
                return
            } ?: return

            // Long running calls such as RunWithResultAndExitCode must not be cut off by the read timeout.
            client.soTimeout = 0
            val response = handleJsonString(request, remote)
            val out = client.getOutputStream()
            out.write(response.toByteArray(StandardCharsets.UTF_8))
            out.write('\n'.code)
            out.flush()
        }
    }

    fun handleJsonString(jsonString: String, client: InetSocketAddress?): String {
        Logger.debug("Received json: $jsonString")
        val response = JSONObject()
        response.put("jsonrpc", "2.0")
        try {
            val request = JSONObject(jsonString)
            response.put("id", parseId(request.opt("id")))
            val method = request.getString("method")
            val params = request.optJSONArray("params") ?: JSONArray()
            val args = RpcArgs((0 until params.length()).map { params.get(it) })
            Logger.info("RPC: $method")
            val result = functions.call(method, args, client)
            // Like SimpleRemote, results from void methods are omitted entirely.
            toJson(result)?.let { response.put("result", it) }
        } catch (e: Throwable) {
            val cause = if (e is InvocationTargetException && e.cause != null) e.cause!! else e
            Logger.error("RPC call failed.", cause)
            if (!response.has("id")) response.put("id", 0)
            response.put("error", cause.toString())
        }
        return response.toString()
    }

    private fun parseId(id: Any?): Int = when (id) {
        is Number -> id.toInt()
        is String -> id.toIntOrNull() ?: 0
        else -> 0
    }

    private fun readLine(stream: InputStream): String? {
        val buffer = ByteArrayOutputStream()
        while (true) {
            val b = stream.read()
            if (b < 0) return if (buffer.size() == 0) null else buffer.toString(StandardCharsets.UTF_8.name())
            if (b == '\n'.code) break
            buffer.write(b)
        }
        return buffer.toString(StandardCharsets.UTF_8.name()).trimEnd('\r')
    }

    companion object {
        // Serializes results the same way Newtonsoft.Json does for SimpleRemote, including
        // byte arrays as base64 strings.
        fun toJson(value: Any?): Any? = when (value) {
            null, Unit -> null
            is ByteArray -> Base64.getEncoder().encodeToString(value)
            is LongArray -> JSONArray(value.toList())
            is IntArray -> JSONArray(value.toList())
            is Array<*> -> JSONArray(value.map { toJson(it) ?: JSONObject.NULL })
            is Collection<*> -> JSONArray(value.map { toJson(it) ?: JSONObject.NULL })
            is Map<*, *> -> JSONObject().apply { value.forEach { (k, v) -> put(k.toString(), toJson(v) ?: JSONObject.NULL) } }
            else -> value
        }
    }
}
