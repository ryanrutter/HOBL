// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent

import java.io.File

// Equivalent of SimpleRemote's SetupProcess().  The argument string is split with .NET rules,
// and the program is resolved from PATH, matching SimpleRemote on Linux and macOS.
object ProcessRunner {
    private val nullDevice = File(if (System.getProperty("os.name").orEmpty().startsWith("Windows")) "NUL" else "/dev/null")

    fun setupProcess(programName: String, args: String?, redirectOutput: Boolean): ProcessBuilder {
        val command = listOf(programName) + ArgumentParser.parse(args)
        Logger.info("Preparing to run '$programName ${args.orEmpty()}'")
        val builder = ProcessBuilder(command)
        if (redirectOutput) {
            builder.redirectErrorStream(true)
        } else {
            builder.redirectOutput(nullDevice)
            builder.redirectError(nullDevice)
        }
        return builder
    }

    // Merges stdout and stderr, one line at a time, the same way SimpleRemote's output handler does.
    fun readOutput(process: Process, output: StringBuilder) {
        process.inputStream.bufferedReader(Charsets.UTF_8).useLines { lines ->
            lines.forEach {
                synchronized(output) { output.append(it).append('\n') }
            }
        }
    }

    fun runWithResultAndExitCode(programName: String, args: String?): Pair<Int, String> {
        val process = setupProcess(programName, args, true).start()
        val output = StringBuilder()
        readOutput(process, output)
        val exitCode = process.waitFor()
        Logger.info("Process $programName has completed with exit code $exitCode.")
        return Pair(exitCode, output.toString())
    }
}
