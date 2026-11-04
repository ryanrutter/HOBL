// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent

import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.ByteArrayOutputStream
import java.io.File
import java.net.InetAddress
import java.net.InetSocketAddress
import java.net.ServerSocket
import java.net.Socket

class FunctionsTest {
    @get:Rule
    val temp = TemporaryFolder()

    // The test JVM's own java executable is a portable program to run on any host OS.
    private val javaExe = File(System.getProperty("java.home"), "bin/java").path

    private class EchoPlugin : Plugin {
        override fun call(method: String, args: RpcArgs): Any? = if (method == "Echo") args.string(0) else null
    }

    private val functions = Functions("9.9.9", "/data/local/tmp/agent.jar") { _, className, _ ->
        if (className != "Test.Echo") throw IllegalArgumentException("Plugin class $className is not supported on Aluminium.")
        EchoPlugin()
    }

    private fun call(method: String, vararg args: Any?): Any? = functions.call(method, RpcArgs(args.toList()), null)

    @Test
    fun runWithResultAndExitCodeReturnsExitCodeAndMergedOutput() {
        // "java -version" prints to stderr, which must be merged into the output.
        val result = call("RunWithResultAndExitCode", javaExe, "-version") as Array<*>
        assertEquals("0", result[0])
        assertTrue(result[1].toString().contains("version"))
    }

    @Test
    fun runWithResultAndExitCodeReportsFailures() {
        val result = call("RunWithResultAndExitCode", javaExe, "-XX:+HoblNoSuchOption") as Array<*>
        assertNotEquals("0", result[0])
    }

    @Test
    fun runWithResultReturnsOutputOnly() {
        assertTrue((call("RunWithResult", javaExe, "-version") as String).contains("version"))
    }

    @Test
    fun runStartsWithoutWaiting() {
        assertEquals(true, call("Run", javaExe, "-version"))
    }

    @Test(expected = java.io.IOException::class)
    fun missingProgramThrows() {
        call("RunWithResultAndExitCode", "hobl_no_such_program", null)
    }

    @Test
    fun jobNotifiesCallerAndReturnsResultEx() {
        ServerSocket(0, 1, InetAddress.getLoopbackAddress()).use { listener ->
            listener.soTimeout = 30_000
            val jobId = call("StartJobWithNotification", "127.0.0.1", listener.localPort.toLong(), javaExe, "Normal", "-version") as Int

            val message = listener.accept().use { it.getInputStream().readBytes().toString(Charsets.US_ASCII) }
            assertEquals("JOB $jobId COMPLETED", message)
            assertEquals(true, call("IsJobComplete", jobId))

            val result = JSONObject(call("GetJobResultEx", jobId) as String)
            assertEquals(0, result.getInt("exitCode"))
            assertTrue(result.getString("output").contains("version"))

            // The job is released after its result is read.
            try {
                call("GetJobResultEx", jobId)
                fail("Expected an invalid job id")
            } catch (e: IllegalStateException) {
                assertEquals("Invalid Job Id", e.message)
            }
        }
    }

    @Test
    fun jobUsesClientAddressWhenCallbackAddressIsBlank() {
        ServerSocket(0, 1, InetAddress.getLoopbackAddress()).use { listener ->
            listener.soTimeout = 30_000
            val client = InetSocketAddress(InetAddress.getLoopbackAddress(), 12345)
            val jobId = functions.call("StartJobWithNotification", RpcArgs(listOf("", listener.localPort, javaExe, "Normal", "-version")), client)
            listener.accept().close()
            assertTrue(functions.getAllJobs().containsKey((jobId as Int).toLong()))
        }
    }

    @Test
    fun startJobAndGetJobResult() {
        val jobId = call("StartJob", javaExe, "-version") as Int
        val deadline = System.currentTimeMillis() + 30_000
        while (!(call("IsJobComplete", jobId) as Boolean) && System.currentTimeMillis() < deadline) Thread.sleep(50)
        assertTrue((call("GetJobResult", jobId) as String).contains("version"))
    }

    @Test
    fun stopJobKillsRunningProcess() {
        // Java's single-file source launcher gives a portable long running process.
        val sleeper = temp.newFile("Sleeper.java")
        sleeper.writeText("class Sleeper { public static void main(String[] a) throws Exception { Thread.sleep(60000); } }")
        val jobId = call("StartJob", javaExe, "\"${sleeper.path}\"") as Int
        assertFalse(call("IsJobComplete", jobId) as Boolean)
        assertEquals(true, call("StopJob", jobId))
        assertFalse(functions.getAllJobs().containsKey(jobId.toLong()))
        try {
            call("StopJob", jobId)
            fail("Expected an invalid job id")
        } catch (e: IllegalStateException) {
            assertEquals("Invalid Job Id", e.message)
        }
    }

    @Test
    fun uploadAndDownloadOverTransferSockets() {
        val src = temp.newFolder("src")
        File(src, "results/data.csv").apply { parentFile!!.mkdirs(); writeText("a,b\n1,2\n") }
        val dest = File(temp.root, "dest")

        // Upload: client streams a tar archive and reads back the byte count.
        val uploadPort = call("Upload", dest.path, true) as Int
        Socket("127.0.0.1", uploadPort).use { socket ->
            TarFunctions.writeFileOrDirectoryToStream(socket.getOutputStream(), src.path)
            val reply = socket.getInputStream().bufferedReader().readLine()
            assertEquals("8", reply)
        }
        assertEquals("a,b\n1,2\n", File(dest, "results/data.csv").readText())

        // Download: server streams a tar archive and reports the total size up front.
        val download = call("Download", File(dest, "results").path) as LongArray
        assertEquals(8L, download[1])
        val received = ByteArrayOutputStream()
        Socket("127.0.0.1", download[0].toInt()).use { it.getInputStream().copyTo(received) }
        val out = temp.newFolder("out")
        TarFunctions.readFileOrDirectoryFromStream(received.toByteArray().inputStream(), out.path)
        assertEquals("a,b\n1,2\n", File(out, "data.csv").readText())
    }

    @Test(expected = java.io.IOException::class)
    fun downloadOfMissingPathThrows() {
        call("Download", File(temp.root, "missing").path)
    }

    @Test
    fun uploadFileAndDownloadFileUseBase64() {
        val path = File(temp.root, "small.bin").path
        assertEquals(3, call("UploadFile", path, "AQID", true))
        assertEquals("AQID", call("DownloadFile", path))
    }

    @Test
    fun versionHeartbeatAndLocation() {
        assertEquals("9.9.9", call("GetVersion"))
        assertEquals(true, call("GetHeartbeat"))
        assertEquals("/data/local/tmp/agent.jar", call("GetServerLocation"))
    }

    @Test
    fun pluginLoadCallAndUnload() {
        assertEquals(true, call("PluginLoad", "Echo", "Test.Echo", ""))
        assertEquals("hi", call("PluginCallMethod", "Echo", "Echo", "hi"))
        assertEquals(true, call("PluginUnload", "Echo"))
        try {
            call("PluginCallMethod", "Echo", "Echo", "hi")
            fail("Expected plugin to be unloaded")
        } catch (e: IllegalStateException) {
            assertTrue(e.message!!.contains("not loaded"))
        }
    }

    @Test(expected = IllegalArgumentException::class)
    fun unsupportedPluginClassIsRejected() {
        call("PluginLoad", "X", "Some.Other.Class", "")
    }

    @Test(expected = IllegalArgumentException::class)
    fun unknownMethodIsRejected() {
        call("NoSuchMethod")
    }
}
