// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class WallpaperToolTest {
    private class Description
    private class Extras
    private class Callback

    @Test
    fun fillsTheAndroid16Signature() {
        // setWallpaper(String name, String callingPackage, WallpaperDescription description, boolean allowBackup,
        //              Bundle extras, int which, IWallpaperManagerCallback completion, int userId)
        val description = Description()
        val extras = Extras()
        val types = arrayOf(String::class.java, String::class.java, Description::class.java, Boolean::class.javaPrimitiveType!!,
            Extras::class.java, Int::class.javaPrimitiveType!!, Callback::class.java, Int::class.javaPrimitiveType!!)
        val args = WallpaperTool.setWallpaperArgs(types, 11, { description }, { extras })
        assertEquals("hobl", args[0])
        assertEquals("com.android.shell", args[1])
        assertNull(args[2])  // Only android.app.wallpaper.WallpaperDescription is built; other types are left null.
        assertEquals(true, args[3])
        assertNull(args[4])
        assertEquals(3, args[5])
        assertNull(args[6])
        assertEquals(11, args[7])
    }

    @Test
    fun fillsTheAndroid15Signature() {
        // setWallpaper(String name, String callingPackage, int[] screenOrientations, List<Rect> crops, boolean allowBackup,
        //              Bundle extras, int which, IWallpaperManagerCallback completion, int userId)
        val types = arrayOf(String::class.java, String::class.java, IntArray::class.java, List::class.java,
            Boolean::class.javaPrimitiveType!!, Extras::class.java, Int::class.javaPrimitiveType!!, Callback::class.java,
            Int::class.javaPrimitiveType!!)
        val args = WallpaperTool.setWallpaperArgs(types, 10, { null }, { Extras() })
        assertArrayEquals(IntArray(0), args[2] as IntArray)
        assertEquals(emptyList<Any>(), args[3])
        assertEquals(true, args[4])
        assertEquals(3, args[6])
        assertEquals(10, args[8])
    }
}
