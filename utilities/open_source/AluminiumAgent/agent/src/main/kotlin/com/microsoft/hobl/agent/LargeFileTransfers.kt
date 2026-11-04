// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent

import java.net.ServerSocket
import java.net.Socket
import java.net.SocketTimeoutException
import java.nio.charset.StandardCharsets

// Mirrors SimpleDUTRemote.HelperFunctions.LargeFileTransfers.  Each transfer uses a one-shot
// listener that the client must connect to within 10 seconds.
object LargeFileTransfers {
    private const val ACCEPT_TIMEOUT_MS = 10 * 1000

    fun upload(path: String, server: ServerSocket, overwrite: Boolean) {
        Logger.info("Waiting for connection for directory transfer on port ${server.localPort}")
        val client = accept(server) ?: return
        client.use {
            try {
                val stream = client.getInputStream()
                val bytesReceived = TarFunctions.readFileOrDirectoryFromStream(stream, path, overwrite)
                Logger.info("Successfully received $bytesReceived bytes, written to $path")

                // Tar writers may pad the archive with extra empty blocks.  Drain them so closing
                // the socket doesn't reset the connection before the client reads the byte count.
                val dummy = ByteArray(1024)
                while (stream.available() > 0) stream.read(dummy)

                client.getOutputStream().write("$bytesReceived\r\n".toByteArray(StandardCharsets.US_ASCII))
                client.getOutputStream().flush()
                client.shutdownOutput()
                client.soTimeout = ACCEPT_TIMEOUT_MS
                try {
                    while (stream.read(dummy) >= 0) { }
                } catch (_: SocketTimeoutException) { }
            } catch (e: Exception) {
                Logger.error("Upload failed.", e)
            }
        }
    }

    fun download(path: String, server: ServerSocket) {
        Logger.info("Waiting for connection for directory transfer on port ${server.localPort}")
        val client = accept(server) ?: return
        client.use {
            try {
                val bytesSent = TarFunctions.writeFileOrDirectoryToStream(client.getOutputStream(), path)
                Logger.info("Successfully sent $bytesSent bytes, read from $path")
            } catch (e: Exception) {
                Logger.error("Download failed", e)
            }
        }
    }

    private fun accept(server: ServerSocket): Socket? {
        server.use {
            server.soTimeout = ACCEPT_TIMEOUT_MS
            return try {
                server.accept()
            } catch (e: SocketTimeoutException) {
                Logger.warn("Timed out waiting for client to begin transferring files. Closing port.")
                null
            }
        }
    }
}
