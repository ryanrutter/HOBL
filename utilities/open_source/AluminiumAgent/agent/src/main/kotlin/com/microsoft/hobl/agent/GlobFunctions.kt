// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent

import java.io.File

// Mirrors SimpleDUTCommonLibrary.GlobFunctions: wildcards are only supported in the last path element.
object GlobFunctions {
    fun isGlob(path: String): Boolean = path.contains('*') || path.contains('?')

    fun glob(path: String): List<File> {
        val target = File(path)
        val parent = target.parentFile ?: File(".")
        val regex = toRegex(target.name)
        return parent.listFiles()
            ?.filter { regex.matches(it.name) }
            ?.sortedBy { it.name }
            ?: emptyList()
    }

    private fun toRegex(pattern: String): Regex {
        val sb = StringBuilder()
        for (c in pattern) {
            when (c) {
                '*' -> sb.append(".*")
                '?' -> sb.append('.')
                else -> sb.append(Regex.escape(c.toString()))
            }
        }
        return Regex(sb.toString())
    }
}
