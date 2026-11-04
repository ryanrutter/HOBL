// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent

import org.json.JSONArray
import org.json.JSONObject

// Positional JSON-RPC parameters with defaults for missing or null values, mirroring how
// SimpleJsonRpc fills optional .NET parameters with Type.Missing.
class RpcArgs(private val values: List<Any?>) {
    val size: Int get() = values.size

    fun raw(index: Int): Any? {
        val value = values.getOrNull(index)
        return if (value == null || value == JSONObject.NULL) null else value
    }

    fun string(index: Int, default: String? = null): String? = raw(index)?.toString() ?: default

    fun requireString(index: Int, name: String): String =
        string(index) ?: throw IllegalArgumentException("Missing required parameter '$name'")

    fun long(index: Int, default: Long = 0): Long = when (val value = raw(index)) {
        null -> default
        is Number -> value.toLong()
        is String -> value.trim().toDouble().toLong()
        else -> throw IllegalArgumentException("Parameter $index is not a number: $value")
    }

    fun double(index: Int, default: Double = 0.0): Double = when (val value = raw(index)) {
        null -> default
        is Number -> value.toDouble()
        is String -> value.trim().toDouble()
        else -> throw IllegalArgumentException("Parameter $index is not a number: $value")
    }

    fun bool(index: Int, default: Boolean = false): Boolean = when (val value = raw(index)) {
        null -> default
        is Boolean -> value
        is Number -> value.toInt() != 0
        is String -> value.equals("true", ignoreCase = true) || value == "1"
        else -> throw IllegalArgumentException("Parameter $index is not a boolean: $value")
    }

    fun longList(index: Int): List<Long> {
        val value = raw(index) ?: throw IllegalArgumentException("Parameter $index is null")
        val array = value as? JSONArray ?: throw IllegalArgumentException("Parameter $index is not a list: $value")
        return (0 until array.length()).map { RpcArgs(listOf(array.get(it))).long(0) }
    }

    fun drop(count: Int): RpcArgs = RpcArgs(values.drop(count))
}

// Equivalent of a SimpleRemote plugin DLL class loaded with PluginLoad().
interface Plugin {
    fun call(method: String, args: RpcArgs): Any?
}
