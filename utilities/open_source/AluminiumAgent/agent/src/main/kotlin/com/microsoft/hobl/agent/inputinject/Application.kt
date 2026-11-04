// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent.inputinject

import com.microsoft.hobl.agent.Plugin
import com.microsoft.hobl.agent.RpcArgs
import org.json.JSONArray
import org.json.JSONObject
import java.io.File

// Android counterpart of InputInject.Application (InputInject/Program.cs).  HOBL loads it with
// PluginLoad("InputInject", "InputInject.Application", ...) and calls it with PluginCallMethod,
// using the same method names and parameter order as the .NET plugin.
class Application(private val interop: Interop) : Plugin {

    override fun call(method: String, args: RpcArgs): Any? = when (method) {
        "Screenshot" -> interop.screenshot(args.double(0), args.double(1), args.double(2, 1.0), args.double(3, 1.0), args.long(4))
        // Continuous capture is not implemented on Aluminium, the same as macOS.
        "ContinuousScreenshot" -> 0
        "WriteCapturesToDisk", "StopCapture", "ClearCaptures" -> null
        "GetScreenWidth" -> interop.getScreenWidth()
        "GetScreenHeight" -> interop.getScreenHeight()
        "GetScreenInfo" -> interop.getScreenInfo()
        "MoveTo" -> interop.moveTo(args.long(0), args.long(1), args.long(2), args.bool(3))
        "MoveBy" -> interop.moveBy(args.long(0), args.long(1), args.bool(2))
        "Tap" -> interop.tap(args.long(0), args.long(1), args.long(2), args.bool(3, true), args.long(4), args.bool(5))
        "TapDown" -> interop.tapDown(args.long(0), args.long(1), args.bool(2, true), args.long(3), args.bool(4))
        "TapUp" -> interop.tapUp(args.long(0), args.long(1), args.bool(2, true), args.long(3), args.bool(4))
        "Path" -> path(args.longList(0), args.longList(1), args.longList(2), args.bool(3, true), args.long(4))
        "Scroll" -> interop.scroll(args.long(0), args.long(1), args.long(2), args.requireString(3, "direction"), args.long(4), args.bool(5))
        "Type" -> interop.type(args.requireString(0, "s"), args.long(1))
        "WindowMove" -> interop.windowMove(args.long(0), args.long(1))
        "WindowMaximize" -> interop.windowMaximize()
        "Process" -> process(args.requireString(0, "args"))
        "EventTag" -> interop.eventTag(args.requireString(0, "tag"))
        "TouchDown" -> interop.touchDown(args.bool(0, true))
        "TouchUp" -> interop.touchUp(args.bool(0, true))
        "MouseWheel" -> interop.mouseWheel(args.long(0).toInt())
        else -> throw IllegalArgumentException("Method $method not found in InputInject.Application.")
    }.let { if (it == Unit) null else it }

    fun path(xList: List<Long>, yList: List<Long>, delayList: List<Long>, primary: Boolean, screenIndex: Long = 0) {
        if (xList.size != yList.size || xList.size != delayList.size) {
            throw IllegalStateException("x, y, and delay lists must have the same length.")
        }
        if (xList.isEmpty()) throw IllegalStateException("item.x is null or empty")
        interop.moveTo(xList[0], yList[0], screenIndex, false)
        interop.touchDown(primary)
        Thread.sleep(delayList[0])
        for (i in 1 until xList.size) {
            interop.moveTo(xList[i], yList[i], screenIndex, false)
            Thread.sleep(delayList[i])
        }
        interop.touchUp(primary)
    }

    // Executes a list of input commands, from a JSON file or string.  Mirrors Application.Process().
    fun process(args: String) {
        val startTime = System.nanoTime()
        val file = File(args)
        val json = if (file.isFile) file.readText() else args
        val items = JSONArray(json)

        for (i in 0 until items.length()) {
            val item = items.getJSONObject(i)
            when (item.optString("cmd")) {
                "tap" -> interop.tap(first(item, "x"), first(item, "y"), first(item, "delay"), item.optBoolean("primary", false))
                "moveby" -> {
                    interop.moveBy(first(item, "x"), first(item, "y"))
                    Thread.sleep(first(item, "delay"))
                }
                "moveto" -> {
                    interop.moveTo(first(item, "x"), first(item, "y"))
                    Thread.sleep(first(item, "delay"))
                }
                "scroll" -> interop.scroll(first(item, "x"), first(item, "y"), first(item, "delay"), item.getString("direction"))
                "type" -> interop.type(item.getString("keys"), first(item, "delay"))
                "windowmove" -> interop.windowMove(first(item, "delay"), item.optString("direction", "0").toLong())
                "path" -> path(list(item, "x"), list(item, "y"), list(item, "delay"), true)
                "sleep" -> Thread.sleep(first(item, "delay"))
                "sleepto" -> Interop.sleepTo(startTime, first(item, "delay"))
                "etw" -> interop.eventTag(item.getString("tag"))
            }
        }
    }

    private fun list(item: JSONObject, key: String): List<Long> {
        val array = item.optJSONArray(key) ?: throw IllegalStateException("item.$key is null or empty")
        return (0 until array.length()).map { array.get(it).toString().toLong() }
    }

    private fun first(item: JSONObject, key: String): Long =
        list(item, key).firstOrNull() ?: throw IllegalStateException("item.$key is null or empty")

    companion object {
        const val CLASS_NAME = "InputInject.Application"

        fun create(): Application = Application(Interop(AndroidEventInjector(), ScreencapSource()))
    }
}
