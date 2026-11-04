// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent

import java.io.EOFException
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.io.InputStream
import java.io.OutputStream
import java.nio.charset.StandardCharsets

// Mirrors SimpleDUTCommonLibrary.TarFunctions.  Streams GNU tar archives compatible with
// Python's tarfile module, which is what HOBL's call_rpc.upload()/download() use.
object TarFunctions {
    private const val BLOCK = 512
    private const val NAME_LENGTH = 100
    private const val GNU_LONGNAME = "././@LongLink"

    fun writeFileOrDirectoryToStream(stream: OutputStream, targetPath: String): Long {
        val rootPath: File?
        val entries: List<File>

        if (GlobFunctions.isGlob(targetPath)) {
            rootPath = File(targetPath).parentFile
            entries = GlobFunctions.glob(targetPath).flatMap { listRecursive(it) }
        } else {
            val target = File(targetPath)
            if (!target.exists()) throw IOException("Path not found: $targetPath")
            if (target.isDirectory) {
                rootPath = target
                entries = target.listFiles()?.sortedBy { it.name }?.flatMap { listRecursive(it) } ?: emptyList()
            } else {
                rootPath = target.parentFile
                entries = listOf(target)
            }
        }

        var bytesSent = 0L
        for (entry in entries) {
            var name = if (rootPath != null) entry.absolutePath.removePrefix(rootPath.absolutePath) else entry.name
            // Tar entry names always use forward slashes, as in SimpleRemote.
            name = name.replace(File.separatorChar, '/').trimStart('/')
            if (entry.isDirectory) name += "/"

            val size = if (entry.isDirectory) 0L else entry.length()
            writeHeader(stream, name, size, entry.isDirectory, entry.canExecute(), entry.lastModified() / 1000)
            if (!entry.isDirectory) {
                entry.inputStream().use { it.copyTo(stream) }
                writePadding(stream, size)
                bytesSent += size
            }
        }

        // End of archive is marked by two empty blocks.
        stream.write(ByteArray(BLOCK * 2))
        stream.flush()
        return bytesSent
    }

    fun readFileOrDirectoryFromStream(stream: InputStream, pathToWrite: String, overwrite: Boolean = true): Long {
        val root = File(pathToWrite).canonicalFile
        var bytesRead = 0L
        var longName: String? = null
        val header = ByteArray(BLOCK)

        while (true) {
            if (!readBlock(stream, header)) break
            if (header.all { it.toInt() == 0 }) break

            val typeFlag = header[156].toInt().toChar()
            val size = parseNumber(header, 124, 12)
            var name = longName ?: headerName(header)
            longName = null

            when (typeFlag) {
                'L' -> {
                    longName = String(readData(stream, size), StandardCharsets.UTF_8).trimEnd('\u0000')
                    continue
                }
                'x' -> {
                    longName = parsePaxPath(String(readData(stream, size), StandardCharsets.UTF_8))
                    continue
                }
                'g' -> {
                    readData(stream, size)
                    continue
                }
            }

            val target = File(root, name).canonicalFile
            if (target != root && !target.path.startsWith(root.path + File.separator)) {
                throw IOException("Tar entry '$name' resolves outside of $pathToWrite")
            }

            if (typeFlag == '5' || name.endsWith("/")) {
                target.mkdirs()
                skipData(stream, size)
            } else if (typeFlag == '0' || typeFlag == '\u0000' || typeFlag == '7') {
                if (target.exists() && !overwrite) throw IOException("File already exists: ${target.path}")
                target.parentFile?.mkdirs()
                FileOutputStream(target).use { copyExactly(stream, it, size) }
                skipPadding(stream, size)
                val mode = parseNumber(header, 100, 8)
                if (mode and 0b001_001_001 != 0L) target.setExecutable(true, false)
                bytesRead += size
            } else {
                // Links and special files are not used by HOBL.
                skipData(stream, size)
            }
        }
        return bytesRead
    }

    private fun listRecursive(file: File): List<File> {
        if (!file.isDirectory) return listOf(file)
        val children = file.listFiles()?.sortedBy { it.name } ?: emptyList()
        return listOf(file) + children.flatMap { listRecursive(it) }
    }

    private fun writeHeader(stream: OutputStream, name: String, size: Long, isDirectory: Boolean, executable: Boolean, mtime: Long) {
        val nameBytes = name.toByteArray(StandardCharsets.UTF_8)
        if (nameBytes.size > NAME_LENGTH) {
            // GNU long name extension: the real name is stored in a preceding pseudo-entry.
            val data = nameBytes + byteArrayOf(0)
            stream.write(buildHeader(GNU_LONGNAME.toByteArray(StandardCharsets.US_ASCII), data.size.toLong(), 'L', 0, 0))
            stream.write(data)
            writePadding(stream, data.size.toLong())
        }
        val mode = if (isDirectory || executable) 0b111_101_101 else 0b110_100_100
        stream.write(buildHeader(nameBytes.copyOf(minOf(nameBytes.size, NAME_LENGTH)), size, if (isDirectory) '5' else '0', mode, mtime))
    }

    private fun buildHeader(name: ByteArray, size: Long, typeFlag: Char, mode: Int, mtime: Long): ByteArray {
        val header = ByteArray(BLOCK)
        System.arraycopy(name, 0, header, 0, name.size)
        writeOctal(header, 100, 8, mode.toLong())
        writeOctal(header, 108, 8, 0)
        writeOctal(header, 116, 8, 0)
        writeOctal(header, 124, 12, size)
        writeOctal(header, 136, 12, mtime)
        header[156] = typeFlag.code.toByte()
        System.arraycopy("ustar  \u0000".toByteArray(StandardCharsets.US_ASCII), 0, header, 257, 8)

        // Checksum is calculated with the checksum field itself treated as spaces.
        for (i in 148 until 156) header[i] = ' '.code.toByte()
        val checksum = header.sumOf { it.toInt() and 0xff }
        val checksumText = String.format("%06o", checksum).toByteArray(StandardCharsets.US_ASCII)
        System.arraycopy(checksumText, 0, header, 148, checksumText.size)
        header[154] = 0
        header[155] = ' '.code.toByte()
        return header
    }

    private fun writeOctal(header: ByteArray, offset: Int, length: Int, value: Long) {
        val text = java.lang.Long.toOctalString(value).padStart(length - 1, '0')
        System.arraycopy(text.toByteArray(StandardCharsets.US_ASCII), 0, header, offset, length - 1)
        header[offset + length - 1] = 0
    }

    private fun headerName(header: ByteArray): String {
        val name = cString(header, 0, NAME_LENGTH)
        // POSIX ustar headers may split long names into a prefix field.
        val magic = String(header, 257, 6, StandardCharsets.US_ASCII)
        if (magic == "ustar\u0000") {
            val prefix = cString(header, 345, 155)
            if (prefix.isNotEmpty()) return "$prefix/$name"
        }
        return name
    }

    private fun cString(bytes: ByteArray, offset: Int, length: Int): String {
        var end = offset
        while (end < offset + length && bytes[end].toInt() != 0) end++
        return String(bytes, offset, end - offset, StandardCharsets.UTF_8)
    }

    private fun parseNumber(header: ByteArray, offset: Int, length: Int): Long {
        // GNU base-256 encoding is flagged by the high bit of the first byte.
        if (header[offset].toInt() and 0x80 != 0) {
            var value = 0L
            for (i in offset + 1 until offset + length) value = (value shl 8) or (header[i].toLong() and 0xff)
            return value
        }
        val text = cString(header, offset, length).trim()
        return if (text.isEmpty()) 0 else text.toLong(8)
    }

    private fun parsePaxPath(records: String): String? {
        // Each record is "<length> <key>=<value>\n".
        for (line in records.split('\n')) {
            val record = line.substringAfter(' ', "")
            if (record.startsWith("path=")) return record.removePrefix("path=")
        }
        return null
    }

    private fun readBlock(stream: InputStream, buffer: ByteArray): Boolean {
        var offset = 0
        while (offset < buffer.size) {
            val count = stream.read(buffer, offset, buffer.size - offset)
            if (count < 0) {
                if (offset == 0) return false
                throw EOFException("Unexpected end of tar stream")
            }
            offset += count
        }
        return true
    }

    private fun readData(stream: InputStream, size: Long): ByteArray {
        val out = java.io.ByteArrayOutputStream()
        copyExactly(stream, out, size)
        skipPadding(stream, size)
        return out.toByteArray()
    }

    private fun skipData(stream: InputStream, size: Long) {
        copyExactly(stream, DiscardStream, size)
        skipPadding(stream, size)
    }

    private fun copyExactly(stream: InputStream, out: OutputStream, size: Long) {
        val buffer = ByteArray(64 * 1024)
        var remaining = size
        while (remaining > 0) {
            val count = stream.read(buffer, 0, minOf(buffer.size.toLong(), remaining).toInt())
            if (count < 0) throw EOFException("Unexpected end of tar stream")
            out.write(buffer, 0, count)
            remaining -= count
        }
    }

    private fun skipPadding(stream: InputStream, size: Long) {
        val padding = paddingFor(size)
        if (padding > 0) copyExactly(stream, DiscardStream, padding.toLong())
    }

    private fun writePadding(stream: OutputStream, size: Long) {
        val padding = paddingFor(size)
        if (padding > 0) stream.write(ByteArray(padding))
    }

    private fun paddingFor(size: Long): Int = ((BLOCK - (size % BLOCK)) % BLOCK).toInt()

    // OutputStream.nullOutputStream() requires API 33, above the agent's minSdk.
    private object DiscardStream : OutputStream() {
        override fun write(b: Int) {}
        override fun write(b: ByteArray, off: Int, len: Int) {}
    }
}
