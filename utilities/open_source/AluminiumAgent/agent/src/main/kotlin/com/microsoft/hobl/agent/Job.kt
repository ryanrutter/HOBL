// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent

import java.net.InetAddress
import java.net.InetSocketAddress
import java.net.Socket
import java.nio.charset.StandardCharsets
import java.util.concurrent.atomic.AtomicInteger

class JobCallbackInfo(val address: InetAddress, val port: Int)

// Mirrors SimpleDUTRemote.JobSystem.Job.  Runs a process in the background, buffers its output,
// and optionally sends "JOB <id> COMPLETED" to the caller when the process exits.
class Job private constructor(val jobId: Int, private val process: Process, private val callback: JobCallbackInfo?) {
    private val output = StringBuilder()
    @Volatile private var done = false
    private var exitCode = 0

    init {
        Thread({
            try {
                ProcessRunner.readOutput(process, output)
                exitCode = process.waitFor()
            } catch (e: Exception) {
                Logger.error("Job $jobId failed while waiting for process.", e)
            }
            done = true
            Logger.info("Job $jobId completed with exit code $exitCode.")
            callback?.let { sendCompletion(it) }
        }, "Job-$jobId").apply { isDaemon = true }.start()
    }

    fun isDone(): Boolean = done

    fun getResult(): String = synchronized(output) { output.toString() }

    fun getExitCode(): Int = exitCode

    fun kill() {
        process.destroyForcibly()
    }

    private fun sendCompletion(info: JobCallbackInfo) {
        // Retry with exponential backoff, in case the host is briefly unreachable.
        var retryAttempt = 0
        while (retryAttempt < MAX_CALLBACK_ATTEMPTS) {
            try {
                Socket().use { socket ->
                    socket.connect(InetSocketAddress(info.address, info.port), NETWORK_TIMEOUT_MS)
                    socket.getOutputStream().write("JOB $jobId COMPLETED".toByteArray(StandardCharsets.US_ASCII))
                    socket.getOutputStream().flush()
                }
                Logger.debug("Successfully sent job completion message for job $jobId")
                return
            } catch (e: Exception) {
                val delaySeconds = 1L shl retryAttempt
                Logger.warn("Failed to send completion message for job $jobId, attempt $retryAttempt: ${e.message}. Retry in $delaySeconds seconds.")
                Thread.sleep(delaySeconds * 1000)
                retryAttempt++
            }
        }
        Logger.error("Unable to send completion message for job $jobId to ${info.address.hostAddress}:${info.port}")
    }

    companion object {
        private const val NETWORK_TIMEOUT_MS = 5000
        private const val MAX_CALLBACK_ATTEMPTS = 5
        private val nextJobId = AtomicInteger(0)

        fun createJob(builder: ProcessBuilder, callback: JobCallbackInfo? = null): Job {
            val id = nextJobId.incrementAndGet()
            Logger.info("Spawning new job id $id; will call ${builder.command().first()}")
            return Job(id, builder.start(), callback)
        }
    }
}
