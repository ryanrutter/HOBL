// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent

import org.json.JSONArray
import org.json.JSONObject
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.net.InetAddress
import java.net.Socket
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

class SimpleRpcServerTest {
    private class TestPlugin : Plugin {
        override fun call(method: String, args: RpcArgs): Any? = when (method) {
            "Void" -> null
            "Bytes" -> byteArrayOf(1, 2, 3)
            "Sum" -> args.long(0) + args.long(1, 10)
            else -> throw IllegalArgumentException("Method $method not found")
        }
    }

    private val functions = Functions("1.2.3", "") { _, _, _ -> TestPlugin() }
    private val server = SimpleRpcServer(functions, AllowList(listOf("192.0.2.10")))

    @After
    fun tearDown() = server.stop()

    private fun request(method: String, params: JSONArray = JSONArray(), id: Any = "1"): JSONObject {
        val payload = JSONObject().put("method", method).put("params", params).put("jsonrpc", "2.0").put("id", id)
        return JSONObject(server.handleJsonString(payload.toString(), null))
    }

    @Test
    fun resultResponseMatchesSimpleRemoteShape() {
        val response = request("GetVersion")
        assertEquals("2.0", response.getString("jsonrpc"))
        // HOBL sends the id as a string; SimpleRemote replies with an integer.
        assertEquals(1, response.get("id"))
        assertEquals("1.2.3", response.getString("result"))
        assertFalse(response.has("error"))
    }

    @Test
    fun errorsAreReportedAsStrings() {
        val response = request("NoSuchMethod")
        assertFalse(response.has("result"))
        assertTrue(response.getString("error").contains("NoSuchMethod not found"))
        assertEquals(1, response.get("id"))
    }

    @Test
    fun malformedJsonReturnsError() {
        val response = JSONObject(server.handleJsonString("{not json", null))
        assertTrue(response.has("error"))
        assertEquals(0, response.get("id"))
    }

    @Test
    fun voidPluginResultsAreOmitted() {
        request("PluginLoad", JSONArray(listOf("T", "Test", "")))
        val response = request("PluginCallMethod", JSONArray(listOf("T", "Void")))
        assertFalse(response.has("result"))
        assertFalse(response.has("error"))
    }

    @Test
    fun byteArraysAreBase64Encoded() {
        request("PluginLoad", JSONArray(listOf("T", "Test", "")))
        assertEquals("AQID", request("PluginCallMethod", JSONArray(listOf("T", "Bytes"))).getString("result"))
    }

    @Test
    fun missingOptionalPluginArgumentsUseDefaults() {
        request("PluginLoad", JSONArray(listOf("T", "Test", "")))
        assertEquals(15, request("PluginCallMethod", JSONArray(listOf("T", "Sum", 5))).getInt("result"))
        assertEquals(15, request("PluginCallMethod", JSONArray(listOf("T", "Sum", 5, JSONObject.NULL))).getInt("result"))
    }

    @Test
    fun arraysAndMapsSerializeAsJson() {
        assertEquals(JSONArray::class.java, SimpleRpcServer.toJson(longArrayOf(1, 2))!!.javaClass)
        assertEquals(JSONArray(listOf("0", "out")).toString(), SimpleRpcServer.toJson(arrayOf("0", "out")).toString())
        assertEquals(true, (SimpleRpcServer.toJson(mapOf(5L to true)) as JSONObject).getBoolean("5"))
    }

    @Test
    fun allowListAlwaysAcceptsLoopbackAndListedHosts() {
        val list = AllowList(listOf("192.0.2.10"))
        assertTrue(list.isAllowed(InetAddress.getLoopbackAddress()))
        assertTrue(list.isAllowed(InetAddress.getByName("192.0.2.10")))
        assertFalse(list.isAllowed(InetAddress.getByName("192.0.2.11")))
        assertTrue(AllowList(emptyList(), allowAny = true).isAllowed(InetAddress.getByName("192.0.2.11")))
    }

    @Test
    fun socketServerAnswersOneRequestPerConnection() {
        val listening = CountDownLatch(1)
        var port = 0
        Thread { server.start(0) { port = it; listening.countDown() } }.apply { isDaemon = true }.start()
        assertTrue(listening.await(10, TimeUnit.SECONDS))

        Socket("127.0.0.1", port).use { socket ->
            socket.getOutputStream().write("{\"method\":\"GetHeartbeat\",\"params\":[],\"jsonrpc\":\"2.0\",\"id\":\"1\"}\r\n".toByteArray())
            val response = socket.getInputStream().readBytes().toString(Charsets.UTF_8)
            // The response is newline terminated, then the server closes the connection.
            assertTrue(response.endsWith("\n"))
            assertEquals(true, JSONObject(response.trim()).getBoolean("result"))
        }
    }

    @Test
    fun clientsNotInAllowListGetAnExplanation() {
        // Loopback is always allowed, so connect through one of this machine's other addresses.
        val address = java.net.NetworkInterface.getNetworkInterfaces().toList()
            .filter { it.isUp && !it.isLoopback }
            .flatMap { it.inetAddresses.toList() }
            .firstOrNull { it is java.net.Inet4Address }
        org.junit.Assume.assumeTrue("No non-loopback IPv4 address", address != null)

        val listening = CountDownLatch(1)
        var port = 0
        Thread { server.start(0) { port = it; listening.countDown() } }.apply { isDaemon = true }.start()
        assertTrue(listening.await(10, TimeUnit.SECONDS))

        Socket(address, port).use { socket ->
            socket.getOutputStream().write("{\"method\":\"GetVersion\",\"params\":[],\"jsonrpc\":\"2.0\",\"id\":\"1\"}\r\n".toByteArray())
            val response = JSONObject(socket.getInputStream().readBytes().toString(Charsets.UTF_8).trim())
            assertFalse(response.has("result"))
            assertTrue(response.getString("error").contains("is not allowed to connect"))
        }
    }
}
