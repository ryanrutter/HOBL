// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent

import android.os.Bundle
import android.os.IBinder
import android.os.ParcelFileDescriptor
import java.io.File
import java.lang.reflect.Method
import kotlin.system.exitProcess

// Sets the wallpaper of an Android user, for al_wallpaper_prep.  Android has no shell command for setting a static
// wallpaper, so this calls the wallpaper service the way WallpaperManager.setStream() does.  It is run as a separate
// program from the agent JAR, as the shell user, which has the SET_WALLPAPER and INTERACT_ACROSS_USERS_FULL
// permissions:
//
//   CLASSPATH=<path>/AluminiumAgent.jar app_process / com.microsoft.hobl.agent.WallpaperTool set <image file> <user>
//   CLASSPATH=<path>/AluminiumAgent.jar app_process / com.microsoft.hobl.agent.WallpaperTool clear <user>
//   CLASSPATH=<path>/AluminiumAgent.jar app_process / com.microsoft.hobl.agent.WallpaperTool info <user>
//
// "info" prints the user's wallpaper id, which the service increments each time the wallpaper changes.
object WallpaperTool {
    // WallpaperManager.FLAG_SYSTEM | WallpaperManager.FLAG_LOCK: the home and lock screen wallpaper.
    private const val WHICH = 3
    private const val CALLING_PACKAGE = "com.android.shell"
    private const val NAME = "hobl"

    @JvmStatic
    fun main(args: Array<String>) {
        try {
            when (args.getOrNull(0)) {
                "set" -> set(File(args.getOrNull(1) ?: usage()), user(args.getOrNull(2)))
                "clear" -> clear(user(args.getOrNull(1)))
                "info" -> println(info(user(args.getOrNull(1))))
                else -> usage()
            }
        } catch (e: Throwable) {
            val cause = (e as? java.lang.reflect.InvocationTargetException)?.targetException ?: e
            System.err.println(" ERROR - ${cause.javaClass.simpleName}: ${cause.message}")
            exitProcess(1)
        }
    }

    private fun usage(): Nothing {
        System.err.println("Usage: WallpaperTool set <image file> <user> | clear <user> | info <user>")
        exitProcess(2)
    }

    private fun user(text: String?): Int = text?.toIntOrNull() ?: usage()

    private fun service(): Any {
        val binder = Class.forName("android.os.ServiceManager").getMethod("getService", String::class.java)
            .invoke(null, "wallpaper") ?: throw IllegalStateException("The wallpaper service isn't running.")
        return Class.forName("android.app.IWallpaperManager\$Stub").getMethod("asInterface", IBinder::class.java)
            .invoke(null, binder) ?: throw IllegalStateException("The wallpaper service isn't available.")
    }

    private fun method(service: Any, name: String): Method =
        service.javaClass.methods.firstOrNull { it.name == name }
            ?: throw IllegalStateException("This Android version's wallpaper service has no $name method.")

    // IWallpaperManager.setWallpaper's parameters differ between Android versions, so they are filled in by type.  For
    // example, Android 16 and later take (String name, String callingPackage, WallpaperDescription description,
    // boolean allowBackup, Bundle extras, int which, IWallpaperManagerCallback completion, int userId), and Android 15
    // takes (String name, String callingPackage, int[] screenOrientations, List<Rect> crops, boolean allowBackup,
    // Bundle extras, int which, IWallpaperManagerCallback completion, int userId).  The last int is the user.
    internal fun setWallpaperArgs(types: Array<Class<*>>, user: Int, description: () -> Any?, bundle: () -> Any): Array<Any?> {
        val lastInt = types.indexOfLast { it == Int::class.javaPrimitiveType }
        var strings = 0
        return Array(types.size) { i ->
            val type = types[i]
            when {
                type == String::class.java -> if (strings++ == 0) NAME else CALLING_PACKAGE
                type == Boolean::class.javaPrimitiveType -> true
                type == Int::class.javaPrimitiveType -> if (i == lastInt) user else WHICH
                type == IntArray::class.java -> IntArray(0)
                List::class.java.isAssignableFrom(type) -> emptyList<Any>()
                type.name == "android.os.Bundle" -> bundle()
                type.name == "android.app.wallpaper.WallpaperDescription" -> description()
                else -> null
            }
        }
    }

    private fun emptyDescription(): Any? {
        val builder = Class.forName("android.app.wallpaper.WallpaperDescription\$Builder")
        return builder.getMethod("build").invoke(builder.getConstructor().newInstance())
    }

    private fun set(image: File, user: Int) {
        if (!image.isFile) throw IllegalArgumentException("$image doesn't exist.")
        val service = service()
        val setWallpaper = method(service, "setWallpaper")
        val args = setWallpaperArgs(setWallpaper.parameterTypes, user, ::emptyDescription) { Bundle() }
        val pfd = setWallpaper.invoke(service, *args) as? ParcelFileDescriptor
            ?: throw IllegalStateException("The wallpaper service didn't accept the wallpaper for user $user.")
        // The service applies the wallpaper when the file it returned is closed.
        ParcelFileDescriptor.AutoCloseOutputStream(pfd).use { out -> image.inputStream().use { it.copyTo(out) } }
        println("Set ${image.name} as the wallpaper of user $user.")
    }

    private fun clear(user: Int) {
        val service = service()
        method(service, "clearWallpaper").invoke(service, CALLING_PACKAGE, WHICH, user)
        println("Restored the default wallpaper of user $user.")
    }

    private fun info(user: Int): String {
        val service = service()
        val id = method(service, "getWallpaperIdForUser").invoke(service, 1, user)
        return "id=$id"
    }
}
