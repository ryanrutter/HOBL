// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent

// Splits an argument string into argv the same way .NET's Process class does on Linux and macOS,
// so that HOBL commands such as ["sh", "-c \"echo ok\""] behave identically to SimpleRemote.
//
// Rules (from .NET ParseArgumentsIntoList):
//   - Whitespace separates arguments, unless inside double quotes.
//   - 2N backslashes followed by a quote produce N backslashes and toggle quoting.
//   - 2N+1 backslashes followed by a quote produce N backslashes and a literal quote.
//   - Backslashes not followed by a quote are literal.
//   - Two consecutive quotes inside a quoted region produce a literal quote.
object ArgumentParser {
    fun parse(arguments: String?): List<String> {
        val result = mutableListOf<String>()
        if (arguments.isNullOrEmpty()) return result

        var i = 0
        val n = arguments.length
        while (i < n) {
            while (i < n && arguments[i].isWhitespace()) i++
            if (i == n) break

            val current = StringBuilder()
            var inQuotes = false
            while (i < n) {
                val c = arguments[i]
                if (c == '\\') {
                    var backslashes = 0
                    while (i < n && arguments[i] == '\\') {
                        backslashes++
                        i++
                    }
                    if (i < n && arguments[i] == '"') {
                        repeat(backslashes / 2) { current.append('\\') }
                        if (backslashes % 2 == 1) {
                            current.append('"')
                            i++
                        }
                    } else {
                        repeat(backslashes) { current.append('\\') }
                    }
                } else if (c == '"') {
                    if (inQuotes && i + 1 < n && arguments[i + 1] == '"') {
                        current.append('"')
                        i += 2
                    } else {
                        inQuotes = !inQuotes
                        i++
                    }
                } else if (c.isWhitespace() && !inQuotes) {
                    break
                } else {
                    current.append(c)
                    i++
                }
            }
            result.add(current.toString())
        }
        return result
    }
}
