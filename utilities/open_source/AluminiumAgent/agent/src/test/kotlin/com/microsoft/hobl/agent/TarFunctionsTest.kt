// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.IOException

class TarFunctionsTest {
    @get:Rule
    val temp = TemporaryFolder()

    private fun roundTrip(source: String, overwrite: Boolean = true): Pair<File, Long> {
        val buffer = ByteArrayOutputStream()
        val sent = TarFunctions.writeFileOrDirectoryToStream(buffer, source)
        val dest = temp.newFolder()
        val received = TarFunctions.readFileOrDirectoryFromStream(ByteArrayInputStream(buffer.toByteArray()), dest.path, overwrite)
        assertEquals(sent, received)
        assertEquals("Archives are a whole number of blocks", 0, buffer.size() % 512)
        return Pair(dest, received)
    }

    @Test
    fun directoryRoundTripPreservesTreeAndContent() {
        val src = temp.newFolder("src")
        File(src, "a.txt").writeText("hello")
        File(src, "sub/deeper").mkdirs()
        File(src, "sub/deeper/b.bin").writeBytes(ByteArray(1500) { it.toByte() })
        File(src, "empty").mkdirs()

        val (dest, bytes) = roundTrip(src.path)

        assertEquals(5L + 1500L, bytes)
        assertEquals("hello", File(dest, "a.txt").readText())
        assertArrayEquals(ByteArray(1500) { it.toByte() }, File(dest, "sub/deeper/b.bin").readBytes())
        assertTrue(File(dest, "empty").isDirectory)
    }

    @Test
    fun singleFileIsStoredByName() {
        val src = temp.newFile("single.log")
        src.writeText("data")
        val (dest, _) = roundTrip(src.path)
        assertEquals("data", File(dest, "single.log").readText())
    }

    @Test
    fun globSelectsMatchingFilesOnly() {
        val src = temp.newFolder("glob")
        File(src, "one.json").writeText("1")
        File(src, "two.json").writeText("2")
        File(src, "skip.txt").writeText("x")
        val (dest, _) = roundTrip(File(src, "*.json").path)
        assertEquals(setOf("one.json", "two.json"), dest.list()!!.toSet())
    }

    @Test
    fun longNamesUseGnuLongLink() {
        val src = temp.newFolder("long")
        val longName = "n".repeat(150) + ".txt"
        File(src, longName).writeText("long")
        val (dest, _) = roundTrip(src.path)
        assertEquals("long", File(dest, longName).readText())
    }

    @Test
    fun existingFileIsNotOverwrittenWhenDisallowed() {
        val src = temp.newFolder("src2")
        File(src, "a.txt").writeText("new")
        val buffer = ByteArrayOutputStream()
        TarFunctions.writeFileOrDirectoryToStream(buffer, src.path)
        val dest = temp.newFolder()
        File(dest, "a.txt").writeText("old")
        try {
            TarFunctions.readFileOrDirectoryFromStream(ByteArrayInputStream(buffer.toByteArray()), dest.path, overwrite = false)
            fail("Expected IOException")
        } catch (e: IOException) {
            assertEquals("old", File(dest, "a.txt").readText())
        }
    }

    @Test
    fun entriesOutsideTheDestinationAreRejected() {
        // Build an archive whose entry tries to escape the destination folder.
        val src = temp.newFolder("evil")
        File(src, "x.txt").writeText("x")
        val buffer = ByteArrayOutputStream()
        TarFunctions.writeFileOrDirectoryToStream(buffer, src.path)
        val bytes = buffer.toByteArray()
        "../x.txt".toByteArray().copyInto(bytes, 0)
        // Recompute the header checksum for the altered name.
        for (i in 148 until 156) bytes[i] = ' '.code.toByte()
        val checksum = (0 until 512).sumOf { bytes[it].toInt() and 0xff }
        String.format("%06o", checksum).toByteArray().copyInto(bytes, 148)

        try {
            TarFunctions.readFileOrDirectoryFromStream(ByteArrayInputStream(bytes), temp.newFolder("dest").path)
            fail("Expected IOException")
        } catch (e: IOException) {
            assertTrue(e.message!!.contains("outside"))
        }
    }

    @Test(expected = IOException::class)
    fun missingPathFails() {
        TarFunctions.writeFileOrDirectoryToStream(ByteArrayOutputStream(), File(temp.root, "missing").path)
    }
}
