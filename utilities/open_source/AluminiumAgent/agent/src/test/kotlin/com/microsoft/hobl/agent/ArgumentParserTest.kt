// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent

import org.junit.Assert.assertEquals
import org.junit.Test

class ArgumentParserTest {
    @Test
    fun splitsOnWhitespace() {
        assertEquals(listOf("-rf", "/data/local/tmp/x"), ArgumentParser.parse("-rf   /data/local/tmp/x"))
    }

    @Test
    fun nullAndEmptyProduceNoArguments() {
        assertEquals(emptyList<String>(), ArgumentParser.parse(null))
        assertEquals(emptyList<String>(), ArgumentParser.parse("   "))
    }

    @Test
    fun quotesGroupArguments() {
        // Same shape HOBL uses for shell commands: ["sh", '-c "echo ok"'].
        assertEquals(listOf("-c", "echo ok"), ArgumentParser.parse("-c \"echo ok\""))
    }

    @Test
    fun escapedQuotesAreLiteral() {
        assertEquals(listOf("--override-string=\"{'a':'b'}\""), ArgumentParser.parse("--override-string=\\\"{'a':'b'}\\\""))
    }

    @Test
    fun backslashesFollowedByQuoteAreHalved() {
        assertEquals(listOf("a\\", "b"), ArgumentParser.parse("\"a\\\\\" b"))
    }

    @Test
    fun backslashesNotBeforeQuoteAreLiteral() {
        assertEquals(listOf("C:\\hobl_bin\\x"), ArgumentParser.parse("C:\\hobl_bin\\x"))
        assertEquals(listOf("a\\\\b c"), ArgumentParser.parse("\"a\\\\b c\""))
    }

    @Test
    fun doubledQuoteInsideQuotesIsLiteral() {
        assertEquals(listOf("say \"hi\""), ArgumentParser.parse("\"say \"\"hi\"\"\""))
    }

    @Test
    fun adjacentQuotedAndUnquotedTextJoin() {
        assertEquals(listOf("--logfile=/a b/c"), ArgumentParser.parse("--logfile=\"/a b\"/c"))
    }
}
