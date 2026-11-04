// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent.inputinject

import android.view.KeyEvent

class KeyStroke(val keyCode: Int, val shifted: Boolean)

// Maps characters to Android key codes for a US keyboard layout, equivalent to the scan code maps in
// InteropWin.cs and InteropMac.cs.  Special keys use the WebDriver/Selenium private-use code points
// (\ue000 - \ue03d) that HOBL scenarios already send on Windows and macOS.
object KeyMap {
    const val SHIFT = '\ue008'
    const val CONTROL = '\ue009'
    const val ALT = '\ue00a'
    const val COMMAND = '\ue03d'
    const val FUNCTION = '\ue03e'

    private val map = HashMap<Char, KeyStroke>()

    init {
        for (c in 'a'..'z') {
            map[c] = KeyStroke(KeyEvent.KEYCODE_A + (c - 'a'), false)
            map[c.uppercaseChar()] = KeyStroke(KeyEvent.KEYCODE_A + (c - 'a'), true)
        }
        for (c in '0'..'9') map[c] = KeyStroke(KeyEvent.KEYCODE_0 + (c - '0'), false)

        // Symbols above numbers.
        "!@#\$%^&*()".forEachIndexed { i, c ->
            map[c] = KeyStroke(if (i == 9) KeyEvent.KEYCODE_0 else KeyEvent.KEYCODE_1 + i, true)
        }

        // Punctuation, unshifted and shifted.
        addPair('-', '_', KeyEvent.KEYCODE_MINUS)
        addPair('=', '+', KeyEvent.KEYCODE_EQUALS)
        addPair('[', '{', KeyEvent.KEYCODE_LEFT_BRACKET)
        addPair(']', '}', KeyEvent.KEYCODE_RIGHT_BRACKET)
        addPair('\\', '|', KeyEvent.KEYCODE_BACKSLASH)
        addPair(';', ':', KeyEvent.KEYCODE_SEMICOLON)
        addPair('\'', '"', KeyEvent.KEYCODE_APOSTROPHE)
        addPair(',', '<', KeyEvent.KEYCODE_COMMA)
        addPair('.', '>', KeyEvent.KEYCODE_PERIOD)
        addPair('/', '?', KeyEvent.KEYCODE_SLASH)
        addPair('`', '~', KeyEvent.KEYCODE_GRAVE)

        map[' '] = KeyStroke(KeyEvent.KEYCODE_SPACE, false)
        map['\b'] = KeyStroke(KeyEvent.KEYCODE_DEL, false)
        map['\t'] = KeyStroke(KeyEvent.KEYCODE_TAB, false)
        map['\n'] = KeyStroke(KeyEvent.KEYCODE_ENTER, false)

        // WebDriver special keys.
        map['\ue003'] = KeyStroke(KeyEvent.KEYCODE_DEL, false)          // Backspace
        map['\ue004'] = KeyStroke(KeyEvent.KEYCODE_TAB, false)          // Tab
        map['\ue006'] = KeyStroke(KeyEvent.KEYCODE_ENTER, false)        // Return
        map['\ue007'] = KeyStroke(KeyEvent.KEYCODE_ENTER, false)        // Enter
        map['\ue00c'] = KeyStroke(KeyEvent.KEYCODE_ESCAPE, false)       // Escape
        map['\ue00d'] = KeyStroke(KeyEvent.KEYCODE_SPACE, false)        // Space
        map['\ue00e'] = KeyStroke(KeyEvent.KEYCODE_PAGE_UP, false)      // Page up
        map['\ue00f'] = KeyStroke(KeyEvent.KEYCODE_PAGE_DOWN, false)    // Page down
        map['\ue010'] = KeyStroke(KeyEvent.KEYCODE_MOVE_END, false)     // End
        map['\ue011'] = KeyStroke(KeyEvent.KEYCODE_MOVE_HOME, false)    // Home
        map['\ue012'] = KeyStroke(KeyEvent.KEYCODE_DPAD_LEFT, false)    // Left
        map['\ue013'] = KeyStroke(KeyEvent.KEYCODE_DPAD_UP, false)      // Up
        map['\ue014'] = KeyStroke(KeyEvent.KEYCODE_DPAD_RIGHT, false)   // Right
        map['\ue015'] = KeyStroke(KeyEvent.KEYCODE_DPAD_DOWN, false)    // Down
        map['\ue016'] = KeyStroke(KeyEvent.KEYCODE_INSERT, false)       // Insert
        map['\ue017'] = KeyStroke(KeyEvent.KEYCODE_FORWARD_DEL, false)  // Delete
        for (i in 0 until 12) map['\ue031' + i] = KeyStroke(KeyEvent.KEYCODE_F1 + i, false)  // F1 - F12
    }

    private fun addPair(plain: Char, shifted: Char, keyCode: Int) {
        map[plain] = KeyStroke(keyCode, false)
        map[shifted] = KeyStroke(keyCode, true)
    }

    fun get(c: Char): KeyStroke = map[c] ?: throw IllegalArgumentException("Unsupported character: $c")
}
