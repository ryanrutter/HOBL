// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent

import java.io.File
import java.io.FileOutputStream
import java.io.PrintStream
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

// Minimal file logger.  Keeps the agent free of third party logging dependencies and
// writes nothing until a log file is configured, so unit tests stay quiet.
object Logger {
    private const val MAX_LOG_BYTES = 10L * 1024 * 1024

    private val format = SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS", Locale.US)
    private var out: PrintStream? = null
    var debugEnabled = false

    @Synchronized
    fun open(path: String) {
        val file = File(path)
        file.parentFile?.mkdirs()
        // Start fresh if the previous log grew too large, to avoid filling the DUT over long rundowns.
        val append = file.length() < MAX_LOG_BYTES
        out = PrintStream(FileOutputStream(file, append), true, "UTF-8")
    }

    fun info(message: String) = write("INFO", message)

    fun warn(message: String) = write("WARN", message)

    fun error(message: String, e: Throwable? = null) {
        write("ERROR", if (e == null) message else "$message\n${e.stackTraceToString()}")
    }

    fun debug(message: String) {
        if (debugEnabled) write("DEBUG", message)
    }

    @Synchronized
    private fun write(level: String, message: String) {
        out?.println("${format.format(Date())} $level $message")
    }
}
