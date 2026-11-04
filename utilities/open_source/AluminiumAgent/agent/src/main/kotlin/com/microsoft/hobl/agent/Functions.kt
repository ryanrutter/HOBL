// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent

import org.json.JSONObject
import java.io.File
import java.io.IOException
import java.net.InetSocketAddress
import java.net.ServerSocket
import java.util.Base64
import java.util.concurrent.ConcurrentHashMap

// Mirrors SimpleDUTRemote.Functions, the set of methods exposed over JSON-RPC.
// Method names, parameter order, and result shapes match SimpleRemote so that HOBL's
// core/call_rpc.py works unchanged.  StartJobWithNotification includes the "priority"
// parameter that HOBL's SimpleRemote build adds.
class Functions(
    private val version: String,
    private val serverLocation: String,
    private val pluginFactory: (identifier: String, className: String, path: String) -> Plugin
) {
    private val jobs = ConcurrentHashMap<Long, Job>()
    private val pluginObjects = ConcurrentHashMap<String, Plugin>()

    fun call(method: String, args: RpcArgs, client: InetSocketAddress?): Any? = when (method) {
        "Run" -> run(args.requireString(0, "programName"), args.string(1))
        "RunWithResult" -> runWithResult(args.requireString(0, "programName"), args.string(1))
        "RunWithResultAndExitCode" -> runWithResultAndExitCode(args.requireString(0, "programName"), args.string(1))
        "StartJob" -> startJob(args.requireString(0, "programName"), args.string(1))
        "StartJobWithNotification" -> startJobWithNotification(
            args.string(0), args.long(1), args.requireString(2, "programName"), args.string(3, "Normal")!!, args.string(4), client
        )
        "IsJobComplete" -> isJobComplete(args.long(0))
        "StopJob" -> stopJob(args.long(0))
        "GetJobResult" -> getJobResult(args.long(0))
        "GetJobResultEx" -> getJobResultEx(args.long(0))
        "GetAllJobs" -> getAllJobs()
        "KillProcess" -> killProcess(args.requireString(0, "processName"))
        "UploadFile" -> uploadFile(args.requireString(0, "filename"), args.requireString(1, "data"), args.bool(2))
        "DownloadFile" -> downloadFile(args.requireString(0, "filename"))
        "Upload" -> upload(args.requireString(0, "path"), args.bool(1), args.long(2))
        "Download" -> download(args.requireString(0, "path"), args.long(1))
        "GetVersion" -> version
        "GetHeartbeat" -> true
        "GetClientIP" -> client?.let { "${it.address.hostAddress}:${it.port}" }
            ?: throw IllegalStateException("There isn't an RPC server running, or a client isn't connected.")
        "GetIsRunningAsAdmin" -> throw UnsupportedOperationException("This function is only supported on Windows OS at this time.")
        "GetServerLocation" -> serverLocation
        "PluginLoad" -> pluginLoad(args.requireString(0, "identifier"), args.requireString(1, "dllClass"), args.string(2, "")!!)
        "PluginCallMethod" -> pluginCallMethod(args.requireString(0, "identifier"), args.requireString(1, "methodName"), args.drop(2))
        "PluginUnload" -> pluginObjects.remove(args.requireString(0, "identifier")) != null
        else -> throw IllegalArgumentException("Rpc method name: $method not found in registered functions.")
    }

    fun run(programName: String, args: String?): Boolean {
        ProcessRunner.setupProcess(programName, args, false).start()
        return true
    }

    fun runWithResult(programName: String, args: String?): String =
        ProcessRunner.runWithResultAndExitCode(programName, args).second

    fun runWithResultAndExitCode(programName: String, args: String?): Array<String> {
        val (exitCode, output) = ProcessRunner.runWithResultAndExitCode(programName, args)
        return arrayOf(exitCode.toString(), output)
    }

    fun startJob(programName: String, args: String?): Int {
        val job = Job.createJob(ProcessRunner.setupProcess(programName, args, true))
        jobs[job.jobId.toLong()] = job
        return job.jobId
    }

    fun startJobWithNotification(
        callbackAddress: String?, callbackPort: Long, programName: String, priority: String, args: String?, client: InetSocketAddress?
    ): Int {
        val address = if (callbackAddress.isNullOrBlank()) {
            client?.address ?: throw IllegalStateException("No callback IP provided, and unable to get current connection data.")
        } else {
            java.net.InetAddress.getByName(callbackAddress)
        }
        if (priority != "Normal") {
            // Android does not allow the shell user to raise priority, and HOBL only uses Normal.
            Logger.info("Process priority '$priority' is not supported on Aluminium; running at default priority.")
        }
        val job = Job.createJob(ProcessRunner.setupProcess(programName, args, true), JobCallbackInfo(address, callbackPort.toInt()))
        jobs[job.jobId.toLong()] = job
        return job.jobId
    }

    fun isJobComplete(jobId: Long): Boolean = getJob(jobId).isDone()

    fun stopJob(jobId: Long): Boolean {
        val job = jobs.remove(jobId) ?: throw IllegalStateException("Invalid Job Id")
        if (job.isDone()) {
            jobs[jobId] = job
            throw IllegalStateException("Job already completed - nothing to kill")
        }
        job.kill()
        return true
    }

    fun getJobResult(jobId: Long): String {
        val job = getCompletedJob(jobId)
        jobs.remove(jobId)
        return job.getResult()
    }

    fun getJobResultEx(jobId: Long): String {
        val job = getCompletedJob(jobId)
        jobs.remove(jobId)
        return JSONObject().put("output", job.getResult()).put("exitCode", job.getExitCode()).toString()
    }

    fun getAllJobs(): Map<Long, Boolean> = jobs.mapValues { it.value.isDone() }

    fun killProcess(processName: String): Boolean {
        ProcessRunner.runWithResultAndExitCode("pkill", "\"$processName\"")
        return true
    }

    fun uploadFile(filename: String, data: String, overwrite: Boolean): Int {
        val file = File(filename)
        if (file.exists() && !overwrite) throw IOException("File already exists: $filename")
        val bytes = Base64.getDecoder().decode(data)
        file.writeBytes(bytes)
        return bytes.size
    }

    fun downloadFile(filename: String): String = Base64.getEncoder().encodeToString(File(filename).readBytes())

    fun upload(path: String, overwrite: Boolean, port: Long = 0): Int {
        val directory = File(path)
        if (!directory.isDirectory && !directory.mkdirs()) {
            throw IOException("Can't create receive directory $path. There was either a permission problem, or the path is invalid.")
        }
        if (!directory.canWrite()) {
            throw IOException("Can't write to $path, there was either a permission problem or the path doesn't exist.")
        }
        val server = openTransferSocket(port)
        Thread({ LargeFileTransfers.upload(path, server, overwrite) }, "Upload").apply { isDaemon = true }.start()
        return server.localPort
    }

    fun download(path: String, port: Long = 0): LongArray {
        val size = if (GlobFunctions.isGlob(path)) {
            GlobFunctions.glob(path).filter { it.isFile }.sumOf { it.length() }
        } else {
            val target = File(path)
            if (!target.exists() || !target.canRead()) {
                throw IOException("Can't read from $path, there was either a permission problem, or the path doesn't exist.")
            }
            if (target.isDirectory) target.walkTopDown().filter { it.isFile }.sumOf { it.length() } else target.length()
        }
        val server = openTransferSocket(port)
        Thread({ LargeFileTransfers.download(path, server) }, "Download").apply { isDaemon = true }.start()
        return longArrayOf(server.localPort.toLong(), size)
    }

    fun pluginLoad(identifier: String, className: String, path: String): Boolean {
        pluginObjects[identifier] = pluginFactory(identifier, className, path)
        return true
    }

    fun pluginCallMethod(identifier: String, methodName: String, args: RpcArgs): Any? {
        val plugin = pluginObjects[identifier]
            ?: throw IllegalStateException("Plugin with identifier $identifier not loaded.")
        return plugin.call(methodName, args)
    }

    private fun openTransferSocket(port: Long): ServerSocket {
        val server = ServerSocket()
        // Matches SimpleRemote, which only sets SO_REUSEADDR when a specific port is requested.
        if (port != 0L) server.reuseAddress = true
        server.bind(InetSocketAddress(port.toInt()), 1)
        return server
    }

    private fun getJob(jobId: Long): Job = jobs[jobId] ?: throw IllegalStateException("Invalid Job Id")

    private fun getCompletedJob(jobId: Long): Job {
        val job = getJob(jobId)
        if (!job.isDone()) throw IllegalStateException("Job has not completed.")
        return job
    }
}
